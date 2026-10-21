# 1. Start from an official image that already has Python 3.12.
FROM python:3.12-slim

# 2. All following commands run inside /app in the image.
WORKDIR /app

# 3. Copy ONLY the requirements first, then install them.
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# 4. Download both models now, so they're baked into the image.
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('all-MiniLM-L6-v2'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

# 5. Copy your code.
COPY src/ src/
COPY scripts/ scripts/
COPY data/ data/

# 6. The API listens on port 8000.
EXPOSE 8000

# 7. What runs when a container starts.
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]