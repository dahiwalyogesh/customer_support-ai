# save as debug4.py and run: python debug4.py
from utils import load_kb
from retrieval import find_best_answer

kb = load_kb()

question = "Can I schedule delivery for next month?"
result = find_best_answer(question, kb)

print(f"Q: {question}")
print(f"Found: {result['found']}")
print(f"Score: {result['confidence_score']}")
print(f"Matched: {result['matched_question']}")