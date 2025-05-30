import os
import json
from pathlib import Path
from input_agent import InputAgent
from parser_agent import ParsingAgent
from preprocessing_agent import PreprocessingAgent
from conversion_agent_csv import JsonToCSVAgent
from conversion_agent_md import convert_preprocessed_to_single_markdown
from conversion_agent_txt import combine_preprocessed_to_single_text

def main():
    # Create necessary directories
    Path("pdfs").mkdir(exist_ok=True)
    Path("csv_output").mkdir(exist_ok=True)

    # 1. Input Agent - Scan PDFs
    print("\n1. Scanning PDFs...")
    input_agent = InputAgent("pdfs")
    pdfs_metadata = input_agent.scan_directory()

    # 2. Parser Agent - Parse PDFs
    print("\n2. Parsing PDFs...")
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    parsing_agent = ParsingAgent(tesseract_cmd=tesseract_path)
    pdf_files = [str(meta.file_path) for meta in pdfs_metadata if meta.is_valid]
    parsed_results = parsing_agent.process_batch(pdf_files)

    # Convert ParsedPDF objects to dictionaries
    parsed_dicts = []
    for result in parsed_results:
        parsed_dict = {
            "file_path": str(result.file_path),
            "total_pages": result.total_pages,
            "combined_text": result.combined_text,
            "metadata": result.metadata,
            "error_message": result.error_message,
            "pages": [{
                "page_number": page.page_number,
                "text_content": page.text_content,
                "tables": page.tables,
                "forms": page.forms,
                "confidence_score": page.confidence_score
            } for page in result.pages]
        }
        parsed_dicts.append(parsed_dict)

    # Save parsed results
    with open("combined_parsed_data.json", 'w', encoding='utf-8') as f:
        json.dump(parsed_dicts, f, indent=2)

    # 3. Preprocessing Agent - Preprocess parsed data
    print("\n3. Preprocessing data...")
    preprocessing_agent = PreprocessingAgent()
    with open("combined_parsed_data.json", 'r', encoding='utf-8') as f:
        parsed_data_list = json.load(f)
    
    results = []
    for pdf_data in parsed_data_list:
        preprocessed = preprocessing_agent.process_parsed_data(pdf_data)
        results.append(preprocessed)
    
    preprocessing_agent.save_results(results, "preprocessed_data.json")

    # 4. Convert to different formats
    print("\n4. Converting to different formats...")
    # To CSV
    converter = JsonToCSVAgent(output_dir="csv_output")
    csv_results = converter.convert_json_file("preprocessed_data.json")

    # To Markdown
    convert_preprocessed_to_single_markdown(
        input_json="preprocessed_data.json",
        output_md="all_pdfs_combined.md"
    )

    # To Text
    combine_preprocessed_to_single_text(
        input_json="preprocessed_data.json",
        output_txt="all_pdfs_combined.txt"
    )

    print("\nProcessing complete! Check the output files:")
    print("- combined_parsed_data.json")
    print("- preprocessed_data.json")
    print("- csv_output/combined_tables.csv")
    print("- all_pdfs_combined.md")
    print("- all_pdfs_combined.txt")

if __name__ == "__main__":
    main() 