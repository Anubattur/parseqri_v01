
# it validates the docs and it's metadata

import os
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import List, Optional, Union

from PyPDF2 import PdfReader

@dataclass
class PDFMetadata:
    """
    Data class to store PDF metadata
    """
    filename: str
    file_path: Path
    file_size: int
    creation_date: datetime
    last_modified: datetime
    md5_hash: str
    is_valid: bool
    error_message: Optional[str] = None
    # Optional: Store number of pages, if you want it in the metadata
    page_count: Optional[int] = None

class InputAgent:
    """
    Agent responsible for:
      - Scanning a directory (and subdirectories) for PDFs,
      - Validating PDFs (checking size, basic header, etc.),
      - Returning PDF metadata (size, MD5, timestamps, etc.).
    """

    def __init__(
        self,
        input_directory: Union[str, Path],
        max_file_size_mb: int = 50,
        max_workers: int = 4
    ):
        self.input_directory = Path(input_directory)
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        self.max_workers = max_workers
        self.processing_queue = Queue()
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Configure logging for the Input Agent
        """
        logger = logging.getLogger('InputAgent')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _calculate_md5(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of file
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _validate_pdf(self, file_path: Path) -> tuple[bool, Optional[str], Optional[int]]:
        """
        Validate if the file is a valid PDF. Return tuple:
          (is_valid, error_message, page_count)

        - Checks if file exists
        - Checks file size
        - Checks PDF header (naive or slightly more flexible)
        - Attempts to read pages with PyPDF2
        """
        page_count = None
        try:
            # 1) Check if file exists
            if not file_path.exists():
                return False, "File does not exist", page_count

            # 2) Check file size
            if file_path.stat().st_size > self.max_file_size:
                return False, (
                    f"File size exceeds maximum limit of {self.max_file_size / 1024 / 1024} MB"
                ), page_count

            # 3) Basic PDF header check
            #    Some PDFs might start with e.g. '%PDF-1.4' or '%PDF-1.7'
            with open(file_path, 'rb') as f:
                header = f.read(5)  # read 5 bytes
                if not header.startswith(b'%PDF'):
                    return False, "Invalid PDF header (missing '%PDF')", page_count

            # 4) Validate PDF content
            #    If the PDF is encrypted or broken, PyPDF2 might fail or ask for a password
            try:
                reader = PdfReader(file_path)
                if reader.is_encrypted:
                    # Attempt to decrypt with an empty password (common case for some PDFs)
                    if reader.decrypt("") != 0:
                        # If it can't decrypt with an empty string, consider it invalid or locked
                        return False, "Encrypted PDF and cannot be read without a password", page_count
                if len(reader.pages) == 0:
                    return False, "PDF has no pages", page_count
                # Optionally get the page count
                page_count = len(reader.pages)

            except Exception as e:
                return False, f"PyPDF2 error: {str(e)}", page_count

            return True, None, page_count

        except Exception as e:
            return False, f"Validation error: {str(e)}", page_count

    def process_single_pdf(self, file_path: Path) -> PDFMetadata:
        """
        Process a single PDF file and return its metadata
        """
        try:
            self.logger.info(f"Processing file: {file_path}")

            # Validate PDF
            is_valid, error_message, page_count = self._validate_pdf(file_path)

            # Get file stats
            stats = file_path.stat()

            metadata = PDFMetadata(
                filename=file_path.name,
                file_path=file_path,
                file_size=stats.st_size,
                creation_date=datetime.fromtimestamp(stats.st_ctime),
                last_modified=datetime.fromtimestamp(stats.st_mtime),
                md5_hash=self._calculate_md5(file_path),
                is_valid=is_valid,
                error_message=error_message,
                page_count=page_count
            )

            if is_valid:
                self.logger.info(f"Successfully processed valid PDF: {file_path}")
            else:
                self.logger.warning(f"Processed invalid PDF: {file_path} => {error_message}")

            return metadata

        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            return PDFMetadata(
                filename=file_path.name,
                file_path=file_path,
                file_size=0,
                creation_date=datetime.now(),
                last_modified=datetime.now(),
                md5_hash="",
                is_valid=False,
                error_message=str(e),
                page_count=None
            )

    def scan_directory(self) -> List[PDFMetadata]:
        """
        Scan the input directory for PDF files and process them in parallel
        Returns: List of PDFMetadata objects
        """
        pdf_files = list(self.input_directory.glob("**/*.pdf"))
        self.logger.info(f"Found {len(pdf_files)} PDF files in '{self.input_directory}'")

        # Process files in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.process_single_pdf, pdf_files))

        valid_pdfs = [pdf for pdf in results if pdf.is_valid]
        invalid_pdfs = [pdf for pdf in results if not pdf.is_valid]

        # Log statistics
        self.logger.info(f"Successfully processed {len(valid_pdfs)} valid PDFs")
        self.logger.info(f"Found {len(invalid_pdfs)} invalid PDFs")

        return results

    def watch_directory(self, callback=None):
        """
        Watch directory for new PDF files (optional feature).
        callback: Function to call when new PDF is detected.
        """
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class PDFHandler(FileSystemEventHandler):
            def __init__(self, input_agent, callback_fn):
                self.input_agent = input_agent
                self.callback_fn = callback_fn

            def on_created(self, event):
                if event.is_directory:
                    return
                if Path(event.src_path).suffix.lower() == '.pdf':
                    metadata = self.input_agent.process_single_pdf(Path(event.src_path))
                    if self.callback_fn:
                        self.callback_fn(metadata)

        event_handler = PDFHandler(self, callback)
        observer = Observer()
        observer.schedule(event_handler, str(self.input_directory), recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

# Example Usage
if __name__ == "__main__":
    source_folder = "pdfs"  # Replace with your folder path
    agent = InputAgent(source_folder)
    pdfs_metadata = agent.scan_directory()

    print("\nValid PDFs Metadata:")
    for metadata in pdfs_metadata:
        if metadata.is_valid:
            print(metadata)
