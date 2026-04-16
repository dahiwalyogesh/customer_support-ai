import re
from rank_bm25 import BM25Okapi
from config import MIN_CONFIDENCE_SCORE


# -----------------------------
# Text processing
# -----------------------------

STOPWORDS = {"i", "my", "do", "you", "is", "a", "the", "an", "to", "in", "it", "of", "and", "or","for", "offer", "scheldule"}

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list[str]:
    tokens = normalize_text(text).split()
    return [t for t in tokens if t not in STOPWORDS]


def build_corpus_text(entry: dict) -> str:
    """
    Combines question field and keywords into one searchable string per KB entry.
    Keywords are repeated to give them more weight.
    """
    question_text = entry.get("question", "")
    keywords = " ".join(entry.get("keywords", []))
    return f"{question_text} {keywords} {keywords}"


# -----------------------------
# BM25 retrieval
# -----------------------------

def build_bm25_index(kb: list):
    """
    Builds a BM25 index from the knowledge base.
    Returns the index and tokenized corpus for reference.
    """
    corpus = [tokenize(build_corpus_text(entry)) for entry in kb]
    index = BM25Okapi(corpus)
    return index, corpus


def find_best_answer(question: str, kb: list) -> dict:
    """
    Finds the best matching KB entry for a given question using BM25 scoring.
    Returns a result dict with found status, answer, source, and score.
    """
    index, _ = build_bm25_index(kb)
    query_tokens = tokenize(question)

    if not query_tokens:
        return {
            "found": False,
            "answer": None,
            "source": None,
            "matched_question": None,
            "confidence_score": 0,
        }

    scores = index.get_scores(query_tokens)
    best_index = int(scores.argmax())
    best_score = round(float(scores[best_index]), 2)
    best_entry = kb[best_index]

    if best_score >= MIN_CONFIDENCE_SCORE:
        return {
            "found": True,
            "answer": best_entry["answer"],
            "source": best_entry["source"],
            "matched_question": best_entry["question"],
            "confidence_score": best_score,
        }

    return {
        "found": False,
        "answer": None,
        "source": None,
        "matched_question": None,
        "confidence_score": best_score,
    }


# -----------------------------
# Order lookup
# -----------------------------

def lookup_order_status(order_id: str, orders: list) -> dict | None:
    order_id = order_id.strip().lower()
    for order in orders:
        if order["order_id"].strip().lower() == order_id:
            return order
    return None