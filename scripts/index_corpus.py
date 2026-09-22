"""Index every PDF in corpus/ into the real database.

Wipes and rebuilds the chunks table each run, so re-running after changing
CHUNK_SIZE or OVERLAP gives a clean index.
"""

from pathlib import Path

from src.pipeline import index_pdf
from src.store import connect, create_table

CORPUS_DIR = Path("corpus")
CHUNK_SIZE = 500
OVERLAP = 50

# 1. Connect to the real database (the default name, no argument needed).
conn = connect()
# 2. Drop the chunks table if it exists, then create it fresh.
#    (Same two lines as the test fixture.)
conn.execute("DROP TABLE IF EXISTS chunks")
create_table(conn)

# 3. For every PDF in CORPUS_DIR, in sorted order:
for pdf_path in sorted(CORPUS_DIR.glob("*.pdf")):

#      - run index_pdf on it
    count = index_pdf(conn, pdf_path, CHUNK_SIZE, OVERLAP)
#      - print the file name and how many chunks it produced
    print(pdf_path.name, count)