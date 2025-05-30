
# docs data fetching

import os
import logging
import pdf2image
import pytesseract
import pdfplumber
import PyPDF2
import numpy as np
import cv2
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import json
from pdf2image import convert_from_path

@dataclass
class ParsedPage:
    """Data class to store parsed content from a single PDF page"""
    page_number: int
    text_content: str
    tables: List[List[List[str]]]
    forms: Dict[str, str]
    images: List[np.ndarray]
    confidence_score: float

@dataclass
class ParsedPDF:
    """Data class to store complete parsed PDF content"""
    file_path: Path
    total_pages: int
    pages: List[ParsedPage]
    combined_text: str               # NEW field for a single text block of all pages
    metadata: Dict[str, str]
    error_message: Optional[str] = None

class ParsingAgent:
    """Agent responsible for extracting content from PDFs (with optional OCR fallback)."""

    def __init__(
        self,
        tesseract_cmd: Optional[str] = None,
        ocr_enabled: bool = True,
        ocr_language: str = 'eng',
        max_workers: int = 4,
        dpi: int = 300,
        enable_gpu: bool = False
    ):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.ocr_enabled = ocr_enabled
        self.ocr_language = ocr_language
        self.max_workers = max_workers
        self.dpi = dpi
        self.enable_gpu = enable_gpu
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure logging for the Parsing Agent"""
        logger = logging.getLogger('ParsingAgent')
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _perform_ocr(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Perform OCR on an image and return (extracted_text, confidence_score).
        """
        try:
            ocr_data = pytesseract.image_to_data(
                image,
                lang=self.ocr_language,
                output_type=pytesseract.Output.DICT
            )
            text_parts = []
            confidence_scores = []
            for i, conf in enumerate(ocr_data['conf']):
                # Some Tesseract versions produce '-1' for ignored tokens
                conf_val = int(conf) if conf.isdigit() else -1
                if conf_val > 0:
                    text_parts.append(ocr_data['text'][i])
                    confidence_scores.append(conf_val)

            text = ' '.join(text_parts)
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            return text, float(avg_confidence)

        except Exception as e:
            self.logger.error(f"OCR error: {str(e)}")
            return "", 0.0

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results (grayscale, threshold, denoise)."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            denoised = cv2.fastNlMeansDenoising(binary)
            return denoised
        except Exception as e:
            self.logger.error(f"Image preprocessing error: {str(e)}")
            return image

    def _extract_text_pdfplumber(self, page) -> str:
        """Extract text from a pdfplumber.Page object."""
        try:
            return page.extract_text() or ""
        except Exception as e:
            self.logger.error(f"pdfplumber text extraction error: {str(e)}")
            return ""

    def _extract_tables(self, page) -> List[List[List[str]]]:
        """Extract tables from a page using pdfplumber."""
        try:
            raw_tables = page.extract_tables()
            cleaned_tables = []
            for table in raw_tables:
                if table:
                    cleaned_table = [
                        [
                            str(cell).strip() if cell else ""
                            for cell in row
                        ]
                        for row in table
                    ]
                    cleaned_tables.append(cleaned_table)
            return cleaned_tables
        except Exception as e:
            self.logger.error(f"Table extraction error: {str(e)}")
            return []

    def _extract_forms(self, page) -> Dict[str, str]:
        """Extract form fields and their values (experimental)."""
        try:
            form_fields = {}
            # pdfplumber pages have 'annotations', but it might not cover all possible PDF forms
            annotations = page.hyperlinks + page.annotations
            for annot in annotations:
                if isinstance(annot, dict) and 'data' in annot:
                    form_fields[annot.get('name', 'unknown')] = annot['data']
            return form_fields
        except Exception as e:
            self.logger.error(f"Form extraction error: {str(e)}")
            return {}

    def _is_encrypted_and_locked(self, pdf_path: Path) -> bool:
        """
        Check if PDF is encrypted. If so, attempt to decrypt with empty password.
        Return True if it's still locked, False otherwise.
        """
        try:
            reader = PyPDF2.PdfReader(pdf_path)
            if reader.is_encrypted:
                result = reader.decrypt("")
                # 'result' can be None or 0 if decryption fails
                if result == 0 or result is None:
                    return True
            return False
        except Exception as e:
            self.logger.warning(f"Failed to check encryption: {e}")
            # If reading fails altogether, treat as locked
            return True

    def process_single_page(self, page, page_number: int) -> ParsedPage:
        """
        Process a single page (text, tables, forms), fallback to OCR if text is minimal.
        """
        try:
            text_content = self._extract_text_pdfplumber(page)
            confidence_score = 1.0  # Default confidence if we trust pdfplumber

            # If OCR is enabled and the extracted text is suspiciously short
            if self.ocr_enabled and len(text_content.strip()) < 50:
                images = pdf2image.convert_from_path(
                    str(page.pdf.stream),
                    dpi=self.dpi,
                    first_page=page_number + 1,
                    last_page=page_number + 1
                )
                if images:
                    image_np = np.array(images[0])
                    processed = self._preprocess_image(image_np)
                    ocr_text, ocr_conf = self._perform_ocr(processed)
                    if len(ocr_text.strip()) > len(text_content.strip()):
                        text_content = ocr_text
                        confidence_score = ocr_conf

            # Extract tables
            tables = self._extract_tables(page)

            # Extract forms
            forms = self._extract_forms(page)

            # Placeholder for images
            # If you want to keep the rasterized page or embedded images, do so here.
            images = []

            return ParsedPage(
                page_number=page_number,
                text_content=text_content,
                tables=tables,
                forms=forms,
                images=images,
                confidence_score=confidence_score
            )
        except Exception as e:
            self.logger.error(f"Error processing page {page_number}: {str(e)}")
            return ParsedPage(
                page_number=page_number,
                text_content="",
                tables=[],
                forms={},
                images=[],
                confidence_score=0.0
            )

    def parse_pdf(self, pdf_path: Union[str, Path]) -> ParsedPDF:
        """
        Parse entire PDF and extract all content, returning a ParsedPDF object.
        Also handles minimal encryption checks. 
        """
        pdf_path = Path(pdf_path)
        self.logger.info(f"Starting to parse PDF: {pdf_path}")

        # Check if encrypted (still locked)
        if self._is_encrypted_and_locked(pdf_path):
            error_msg = "PDF is encrypted and cannot be parsed without a password"
            self.logger.error(f"{pdf_path} => {error_msg}")
            return ParsedPDF(
                file_path=pdf_path,
                total_pages=0,
                pages=[],
                combined_text="",
                metadata={},
                error_message=error_msg
            )

        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata = pdf.metadata or {}
                all_pages = []
                for i, page in enumerate(pdf.pages):
                    parsed_page = self.process_single_page(page, i)
                    all_pages.append(parsed_page)

                # Build a single text block from all pages
                combined_text_parts = []
                for p in all_pages:
                    # Optionally add page markers if you want
                    combined_text_parts.append(p.text_content)
                combined_text = "\n".join(combined_text_parts)

                return ParsedPDF(
                    file_path=pdf_path,
                    total_pages=len(pdf.pages),
                    pages=all_pages,
                    combined_text=combined_text,
                    metadata=metadata,
                    error_message=None
                )
        except Exception as e:
            error_msg = f"Error parsing PDF {pdf_path}: {str(e)}"
            self.logger.error(error_msg)
            return ParsedPDF(
                file_path=pdf_path,
                total_pages=0,
                pages=[],
                combined_text="",
                metadata={},
                error_message=error_msg
            )

    def process_batch(self, pdf_paths: List[Union[str, Path]]) -> List[ParsedPDF]:
        """
        Parse multiple PDFs in parallel and return a list of ParsedPDF objects.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.parse_pdf, pdf_paths))
        return results

    def save_results(self, parsed_pdf: ParsedPDF, output_path: Union[str, Path]):
        """
        Save a single PDF's parsed data to a JSON file. 
        If you prefer a combined JSON for all PDFs, handle that outside this method.
        """
        output_path = Path(output_path)

        # Build a dict structure for the entire PDF
        pdf_dict = {
            "original_file": str(parsed_pdf.file_path),
            "total_pages": parsed_pdf.total_pages,
            "combined_text": parsed_pdf.combined_text,  # NEW field
            "metadata": parsed_pdf.metadata,
            "error_message": parsed_pdf.error_message,
            "pages": []
        }
        for page in parsed_pdf.pages:
            pdf_dict["pages"].append({
                "page_number": page.page_number,
                "text_content": page.text_content,
                "tables": page.tables,
                "forms": page.forms,
                "confidence_score": page.confidence_score
                # If you store images, you'd handle them here
            })

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(pdf_dict, f, indent=2, ensure_ascii=False)

# -----------------------------
#       Example Usage
# -----------------------------
if __name__ == "__main__":
    source_folder = "pdfs"  # Replace with your PDF folder path
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update for your system if needed

    parsing_agent = ParsingAgent(tesseract_cmd=tesseract_path)

    # Gather all PDFs in the source folder
    pdf_files = [
        os.path.join(source_folder, file)
        for file in os.listdir(source_folder)
        if file.lower().endswith(".pdf")
    ]

    # Parse each PDF (potentially in parallel)
    results = parsing_agent.process_batch(pdf_files)

    # Example: Save both individual and combined JSON
    all_parsed_pdfs = []
    for parsed_pdf in results:
        if parsed_pdf.error_message:
            print(f"Error parsing {parsed_pdf.file_path}: {parsed_pdf.error_message}")
        else:
            # Save each PDF's data to a separate JSON
            single_output_path = parsed_pdf.file_path.with_suffix('.json')
            parsing_agent.save_results(parsed_pdf, single_output_path)
            print(f"Saved parsed data for {parsed_pdf.file_path} to {single_output_path}")

        # Build a dict version of the parsed PDF for combined JSON
        pdf_dict = {
            "original_file": str(parsed_pdf.file_path),
            "total_pages": parsed_pdf.total_pages,
            "combined_text": parsed_pdf.combined_text,
            "metadata": parsed_pdf.metadata,
            "error_message": parsed_pdf.error_message,
            "pages": []
        }
        for page in parsed_pdf.pages:
            pdf_dict["pages"].append({
                "page_number": page.page_number,
                "text_content": page.text_content,
                "tables": page.tables,
                "forms": page.forms,
                "confidence_score": page.confidence_score
            })
        all_parsed_pdfs.append(pdf_dict)

    # Save a combined JSON of all parsed PDFs
    combined_output_path = "combined_parsed_data.json"
    with open(combined_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_parsed_pdfs, f, indent=2, ensure_ascii=False)

    print(f"Saved combined parsed data for all PDFs to {combined_output_path}")
