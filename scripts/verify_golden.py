"""Check that each golden-dataset entry's page really contains its answer.

Run:  python -m scripts.verify_golden
"""
import csv
import re

from src.extraction import extract_pages
from pathlib import Path
from src.evaluation import page_number

GOLDEN_PATH = "data/golden.csv"
CORPUS_DIR = "corpus"



def main() -> None:
    """Print each entry's claimed page so it can be checked by eye."""
    # 1. Open GOLDEN_PATH with encoding="utf-8-sig" and read it with
    #    csv.DictReader into a list of rows.
    # 2. For each row:
    #    a. Build the PDF path from CORPUS_DIR and row["source_doc"].
    #    b. Call extract_pages(path) to get a list of page strings.
    #    c. Get the page number from row["source_loc"] via page_number().
    #    d. Index into the page list to get that page's text.
    #    e. Print row["id"], row["answer"], and the first 300 characters
    #       of the page text, separated by blank lines.
    
    rows = list(csv.DictReader(open(GOLDEN_PATH, encoding="utf-8-sig")))
    for row in rows:
        pdf_path = Path(f"{CORPUS_DIR}/{row['source_doc']}")
        pages = extract_pages(pdf_path)
        page_num = page_number(row["source_loc"])
        page_text = pages[page_num - 1]
        print(row["id"], row["answer"], page_text)

if __name__ == "__main__":
    main()