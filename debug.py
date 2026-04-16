# save as debug.py and run: python debug.py
from utils import load_kb
from retrieval import find_best_answer

kb = load_kb()

fallback_questions = [
    "Tell me about warranty extensions",
    "Do you offer gift wrapping?",
    "Can I subscribe for monthly deliveries?",
]

for q in fallback_questions:
    result = find_best_answer(q, kb)
    print(f"Q: {q}")
    print(f"   Found: {result['found']}")
    print(f"   Score: {result['confidence_score']}")
    print(f"   Matched: {result['matched_question']}")
    print()