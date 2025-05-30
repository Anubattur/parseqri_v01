import json
import logging
from pathlib import Path
from typing import List, Dict, Any

def convert_preprocessed_to_single_markdown(
    input_json: str = "preprocessed_data.json",
    output_md: str = "all_pdfs_combined.md",
    skip_error_pdfs: bool = True
):
    """
    Reads 'preprocessed_data.json' (an array of PDF dictionaries) and converts
    each PDF's text to a single Markdown file, separated by headings.
    
    :param input_json:    Path to the preprocessed JSON file.
    :param output_md:     Output Markdown file containing all PDFs' text.
    :param skip_error_pdfs: If True, we skip PDFs that have an error_message.
                            If False, we still include them, but show a warning.
    """

    logger = logging.getLogger("MarkdownConverter")
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    input_path = Path(input_json)
    output_path = Path(output_md)

    if not input_path.exists():
        logger.error(f"Input JSON file not found: {input_path}")
        return

    # 1. Load the JSON array
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data_list = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Could not parse JSON: {e}")
        return

    if not isinstance(data_list, list):
        logger.error("The input JSON must be a list of PDF dictionaries.")
        return

    # 2. Open the output Markdown file
    with open(output_path, "w", encoding="utf-8") as md_file:
        # Write a top-level heading
        md_file.write("# All Preprocessed PDFs\n\n")

        # 3. Loop over each PDF dictionary
        for i, pdf_dict in enumerate(data_list, start=1):
            original_file = pdf_dict.get("original_file", f"UnknownFile_{i}")
            error_msg = pdf_dict.get("error_message", "")
            cleaned_text = pdf_dict.get("cleaned_text", "")

            if error_msg and skip_error_pdfs:
                # Skip PDFs with errors
                logger.warning(f"Skipping PDF #{i} due to error: {error_msg}")
                continue
            elif error_msg and not skip_error_pdfs:
                # Include a note in the output if we don't skip
                cleaned_text += f"\n\n**Warning**: This PDF had an error => {error_msg}\n"

            # Handle empty text
            if not cleaned_text.strip():
                logger.warning(f"No text found for PDF #{i} ({original_file}).")
                cleaned_text = "[EMPTY TEXT]\n"

            # 4. Write a heading for this PDF
            md_file.write(f"\n\n---\n\n")  # A horizontal rule
            md_file.write(f"## PDF {i}: {original_file}\n\n")

            # 5. Include the text
            # If you want to treat it as a code block, do triple backticks:
            # md_file.write("```\n" + cleaned_text + "\n```\n")
            # Otherwise, just write it out:
            md_file.write(cleaned_text + "\n")

    logger.info(f"Markdown file created at: {output_path}")

# -----------------------------
#       Example Usage
# -----------------------------
if __name__ == "__main__":
    # Generate one Markdown file for all PDFs, skipping PDFs that have an error_message
    convert_preprocessed_to_single_markdown(
        input_json="preprocessed_data.json",
        output_md="all_pdfs_combined.md",
        skip_error_pdfs=True
    )
