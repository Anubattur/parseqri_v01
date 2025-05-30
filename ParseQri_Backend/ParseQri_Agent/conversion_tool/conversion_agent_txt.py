import json
from pathlib import Path

def combine_preprocessed_to_single_text(
    input_json: str = "preprocessed_data.json",
    output_txt: str = "all_pdfs_combined.txt"
):
    """
    Reads preprocessed_data.json (an array of PDF dictionaries) and combines
    all 'cleaned_text' fields into one text file, separated by headings.
    """

    input_path = Path(input_json)
    output_path = Path(output_txt)

    # 1) Load the JSON array
    with open(input_path, "r", encoding="utf-8") as f:
        data_list = json.load(f)

    # Sanity check
    if not isinstance(data_list, list):
        raise ValueError("The input JSON must be a list of PDF dictionaries.")

    # 2) Create/overwrite the combined text file
    with open(output_path, "w", encoding="utf-8") as out_file:
        # 3) Loop over each PDF in the JSON
        for i, pdf_dict in enumerate(data_list, start=1):
            # Retrieve the original file name (or use a fallback)
            original_file = pdf_dict.get("original_file", f"Unknown_{i}")
            # Extract the cleaned text
            cleaned_text = pdf_dict.get("cleaned_text", "")

            # 4) Write a heading so we know which PDF this text came from
            out_file.write(f"\n\n===== PDF {i}: {original_file} =====\n\n")

            # 5) Write the main text content
            out_file.write(cleaned_text)

    print(f"Successfully combined all PDFs' text into: {output_path}")

# -----------------------------
#       Example Usage
# -----------------------------
if __name__ == "__main__":
    # Default usage:
    combine_preprocessed_to_single_text(
        input_json="preprocessed_data.json",
        output_txt="all_pdfs_combined.txt"
    )
