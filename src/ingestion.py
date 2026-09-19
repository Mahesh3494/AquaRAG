from pathlib import Path

from src.chunking import chunk_text
from src.extraction import extract_pages

def build_chunks(pdf_path: Path, chunk_size: int, overlap: int) -> list[dict]:
    """Extract a PDF and split each page into chunks with metadata.

    Each page is chunked separately, so a chunk never spans two pages and
    every chunk knows which page it came from.

    Args:
        pdf_path: Path to the PDF file.
        chunk_size: Maximum characters per chunk.
        overlap: Characters each chunk repeats from the previous one.

    Returns:
        A list of records in document order. Each record has:
            text         - the chunk's text
            source_doc   - the PDF's filename (not the full path)
            page         - PDF page number, counting from 1
            chunk_index  - position within that page, counting from 0

        Pages that are blank or whitespace-only contribute no records.
    """

    # 1. Get the pages via extract_pages.
    pages = extract_pages(pdf_path)
    
    # 2. Make an empty list for the records.
    records = []

    # 3. For each page, with its position:
    for page_index, page_text in enumerate(pages):
    #      - skip it if the text is blank once stripped
        if not page_text.strip():
            continue

    #      - chunk the page text with chunk_text
        chunks = chunk_text(page_text, chunk_size, overlap)

    #      - for each chunk, with its position, append a record dict
    #        (remember: page number is the page's position + 1)
        for chunk_index, chunk in enumerate(chunks) :
            records.append({
                "text": chunk,
                "source_doc": pdf_path.name,
                "page": page_index + 1,
                "chunk_index": chunk_index
            })
    # 4. Return the records.
    return records