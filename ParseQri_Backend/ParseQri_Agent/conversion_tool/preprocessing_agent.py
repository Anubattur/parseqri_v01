
# data cleaning and preproccessing to create a json formatted data

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import logging

@dataclass
class PreprocessedData:
    """Data class to store preprocessed content"""
    original_file_path: Path
    cleaned_text: str
    structured_text: Dict[str, Any]
    normalized_tables: List[pd.DataFrame]
    extracted_entities: Dict[str, List[str]]
    form_data: Dict[str, Any]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None

class PreprocessingAgent:
    """Agent responsible for preprocessing parsed PDF content"""

    def __init__(
        self,
        language: str = 'en',
        enable_ner: bool = False,
        date_formats: List[str] = None,
        custom_patterns: Dict[str, str] = None
    ):
        self.language = language
        self.enable_ner = enable_ner
        self.date_formats = date_formats or [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
            '%d-%m-%Y', '%m-%d-%Y', '%b %d, %Y', '%d %b %Y'
        ]
        self.custom_patterns = custom_patterns or {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Configure logging for the Preprocessing Agent"""
        logger = logging.getLogger('PreprocessingAgent')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Remove weird punctuation (except some basics)
        text = re.sub(r'[^\w\s.,!?/-]', '', text)
        return text.strip()

    def _normalize_dates(self, text: str) -> str:
        """Normalize date formats in text (simple demonstration)"""
        # NOTE: This is a simplistic approach and may cause false positives.
        # Adjust as needed or use a dateparser library for robust date handling.
        try:
            # Generic pattern to match something like 01/02/2024, 2024-03-15, etc.
            pattern = r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}'
            matches = re.findall(pattern, text)
            for date_str in matches:
                for date_format in self.date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, date_format)
                        # Replace the found date string with a standardized format (YYYY-MM-DD)
                        text = text.replace(date_str, parsed_date.strftime('%Y-%m-%d'))
                        break  # Once we succeed, break from date_formats loop
                    except ValueError:
                        continue
            return text
        except Exception as e:
            self.logger.warning(f"Date normalization error: {e}")
            return text

    def _normalize_table(self, table: List[List[str]]) -> pd.DataFrame:
        """Convert a 2D list to pandas DataFrame with cleaned headers and cells."""
        if not table:
            return pd.DataFrame()
        
        try:
            # First row is the header
            headers = [str(col).strip() for col in table[0]]
            data_rows = table[1:] if len(table) > 1 else []
            df = pd.DataFrame(data_rows, columns=headers)

            # Clean up column names
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]

            # Replace NaN with "" and convert all cells to string
            df = df.fillna("").astype(str)

            # Strip whitespace from each cell in every column
            df = df.apply(lambda col: col.str.strip())

            return df
        except Exception as e:
            self.logger.warning(f"Table normalization error: {e}")
            return pd.DataFrame()

    def _simple_sentence_split(self, text: str) -> List[str]:
        """Simple sentence tokenization by punctuation + whitespace."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def process_parsed_data(self, pdf_data: Dict) -> PreprocessedData:
        """
        Process a single PDF dictionary (from combined_parsed_data.json)
        and return a PreprocessedData object.
        """
        try:
            # 1) Gather all text & tables from the PDF's pages
            all_text_parts = []
            all_tables_raw = []
            all_forms = {}

            pages = pdf_data.get('pages', [])
            for page in pages:
                # Collect text
                page_text = page.get('text_content', '')
                all_text_parts.append(page_text)

                # Collect tables (list of 2D arrays)
                page_tables = page.get('tables', [])
                for t in page_tables:
                    all_tables_raw.append(t)

                # Optionally gather forms
                page_forms = page.get('forms', {})
                # Merge form fields into a single dict, if needed
                for key, val in page_forms.items():
                    all_forms[key] = val

            # 2) Combine all text into one big string
            all_text = " ".join(all_text_parts)
            cleaned_text = self._clean_text(all_text)
            cleaned_text = self._normalize_dates(cleaned_text)

            # 3) Normalize all tables into DataFrames
            normalized_tables = []
            for raw_table in all_tables_raw:
                norm_table_df = self._normalize_table(raw_table)
                if not norm_table_df.empty:
                    normalized_tables.append(norm_table_df)

            # 4) Build simple structured text
            structured_text = {
                'sentences': self._simple_sentence_split(cleaned_text),
                'word_count': len(cleaned_text.split()),
                'sections': {}
            }

            return PreprocessedData(
                original_file_path=Path(pdf_data.get('original_file', '')),
                cleaned_text=cleaned_text,
                structured_text=structured_text,
                normalized_tables=normalized_tables,
                extracted_entities={},    # or fill in if you do NER
                form_data=all_forms,
                metadata=pdf_data.get('metadata', {}),
                error_message=pdf_data.get('error_message', None)
            )
        except Exception as e:
            self.logger.error(f"Error preprocessing PDF data: {e}")
            return PreprocessedData(
                original_file_path=Path(pdf_data.get('original_file', '')),
                cleaned_text="",
                structured_text={},
                normalized_tables=[],
                extracted_entities={},
                form_data={},
                metadata=pdf_data.get('metadata', {}),
                error_message=str(e)
            )

    def save_results(self, preprocessed_data_list: List[PreprocessedData], output_path: Union[str, Path]):
        """
        Save a list of PreprocessedData objects to one JSON file.
        Each PDF becomes one object in the final JSON array.
        """
        output_path = Path(output_path)
        
        try:
            serializable_results = []
            for data in preprocessed_data_list:
                tables_serialized = []
                for df in data.normalized_tables:
                    tables_serialized.append({
                        'columns': df.columns.tolist(),
                        'data': df.values.tolist()
                    })
                
                pdict = {
                    'original_file': str(data.original_file_path),
                    'cleaned_text': data.cleaned_text,
                    'structured_text': data.structured_text,
                    'tables': tables_serialized,
                    'metadata': data.metadata,
                    'error_message': data.error_message
                }
                serializable_results.append(pdict)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Preprocessed data saved to {output_path}")
        except Exception as e:
            raise RuntimeError(f"Error saving results to {output_path}: {str(e)}")

# -----------------------------
#       Example Usage
# -----------------------------
if __name__ == "__main__":
    preprocessing_agent = PreprocessingAgent()
    
    input_json_path = 'combined_parsed_data.json'   # Output from your parser_agent
    output_json_path = 'preprocessed_data.json'

    # Load the array of PDFs from the combined JSON
    with open(input_json_path, 'r', encoding='utf-8') as f:
        parsed_data_list = json.load(f)

    if isinstance(parsed_data_list, list):
        # Process each PDF dictionary in the list
        results = []
        for pdf_data in parsed_data_list:
            preprocessed = preprocessing_agent.process_parsed_data(pdf_data)
            results.append(preprocessed)

        # Save all preprocessed PDFs in one JSON
        preprocessing_agent.save_results(results, output_json_path)
        print(f"Preprocessing complete. Output at {output_json_path}")
    else:
        print("Invalid input format! Expected a list of PDF data.")
