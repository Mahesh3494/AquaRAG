from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

_model = None

def get_model() -> SentenceTransformer:

    """Load the embedding model once and reuse it.

    Loading takes a few seconds, so the model is kept in a module-level
    variable instead of being rebuilt on every call.
    """

    # 1. Declare _model as global so you can rebind it here.
    global _model
    # 2. If _model is None, load SentenceTransformer(MODEL_NAME) into it.
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    # 3. Return _model.
    return _model    

def embed_texts(texts: list[str]) -> list[list[float]]:
    # 1. Return an empty list if texts is empty — the model errors on an
    if not texts:
        #empty batch.
        return []
    # 2. Get the model.
    model = get_model()
    # 3. Call model.encode(texts). It returns a numpy array, one row per text.
    vectors = model.encode(texts)
    # 4. Convert to plain Python lists with .tolist() and return.
    return vectors.tolist()