from pathlib import Path
from pypdf import PdfReader

def extract_pages(pdf_path: Path) -> list[str]:
    """Extract text from a PDF, one string per page.

    Text is returned exactly as pypdf produces it — no cleaning, no
    whitespace normalisation. Cleaning is a Phase 2 experiment that gets
    measured, not a silent step here.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        One string per page, in page order. Index 0 is page 1. A page with
        no extractable text contributes an empty string, so the list length
        always equals the page count.

    Raises:
        FileNotFoundError: If pdf_path does not exist.
    """

    # 1. Raise FileNotFoundError if the path does not exist.
    if not pdf_path.exists():
        raise FileNotFoundError(f"No file found at {pdf_path}")

    # 2. Open the PDF with PdfReader.
    reader = PdfReader(pdf_path)

    # 3. Walk reader.pages...
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        pages.append(text)

    # 4. Return the collected list.
    return pages