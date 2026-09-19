from src.embeddings import EMBEDDING_DIM, embed_texts


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b)


def test_returns_one_vector_per_text():
    assert len(embed_texts(["hello", "world", "again"])) == 3


def test_vectors_have_the_expected_dimension():
    vectors = embed_texts(["hello"])
    assert len(vectors[0]) == EMBEDDING_DIM


def test_empty_input_returns_empty_list():
    assert embed_texts([]) == []


def test_same_text_gives_the_same_vector():
    first = embed_texts(["dissolved oxygen"])[0]
    second = embed_texts(["dissolved oxygen"])[0]
    assert first == second


def test_related_texts_are_closer_than_unrelated_ones():
    answer, question, unrelated = embed_texts([
        "The optimal pH range for fish is from 6.5 to 8.5.",
        "What pH should the water be for fish?",
        "Tractors are used for ploughing agricultural fields.",
    ])
    assert cosine(answer, question) > cosine(answer, unrelated)