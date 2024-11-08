import os
import argparse
import glob
import shutil
from denser_chat.indexer import Indexer
from denser_chat.processor import PDFPassageProcessor


def process_single_pdf(input_pdf, output_dir):
    # Get base name of PDF file without extension
    base_name = os.path.splitext(os.path.basename(input_pdf))[0]

    # Define paths for this specific PDF
    passage_file = os.path.join(output_dir, f"{base_name}_passages.jsonl")
    annotated_pdf = os.path.join(output_dir, f"{base_name}_annotated.pdf")

    # Process the PDF
    processor = PDFPassageProcessor(input_pdf, 1000)
    passages = processor.process_pdf(annotated_pdf, passage_file)
    print(f"Processed {len(passages)} passages from {input_pdf}")

    return passage_file


def concatenate_passage_files(output_dir):
    """Concatenate all individual passage files into one final passages.jsonl"""
    final_passage_file = os.path.join(output_dir, "passages.jsonl")

    # Use 'with' statement to ensure files are properly closed
    with open(final_passage_file, 'w') as outfile:
        # Find all individual passage files
        passage_files = glob.glob(os.path.join(output_dir, "*_passages.jsonl"))

        # Read and write content from each file
        for passage_file in passage_files:
            with open(passage_file, 'r') as infile:
                shutil.copyfileobj(infile, outfile)

    return final_passage_file


def main(input_pdfs, output_dir, index_name):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each PDF file
    passage_files = []
    for pdf_file in input_pdfs:
        if not os.path.exists(pdf_file):
            print(f"Warning: PDF file {pdf_file} does not exist. Skipping.")
            continue

        passage_file = process_single_pdf(pdf_file, output_dir)
        passage_files.append(passage_file)

    if not passage_files:
        print("No PDF files were successfully processed.")
        return

    # Concatenate all passage files into one
    final_passage_file = concatenate_passage_files(output_dir)
    print(f"Created combined passage file: {final_passage_file}")

    # Index the combined passages
    indexer = Indexer(index_name)
    indexer.index(final_passage_file)
    print(f"Indexed passages to {index_name}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process multiple PDFs and create an index.")

    parser.add_argument(
        'input_pdfs',
        type=str,
        nargs='+',
        help="Paths to the input PDF files. Can specify multiple files."
    )
    parser.add_argument(
        'output_dir',
        type=str,
        help="Directory where output files (passages and annotated PDFs) will be stored."
    )
    parser.add_argument(
        'index_name',
        type=str,
        help="Name for the index to be created."
    )

    args = parser.parse_args()

    main(args.input_pdfs, args.output_dir, args.index_name)