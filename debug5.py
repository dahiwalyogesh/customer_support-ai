# save as debug5.py and run: python debug5.py
from utils import load_kb
from retrieval import find_best_answer

kb = load_kb()

faq_edge = [
    "What are the returns like?",
    "How fast is delivery?",
    "Is international delivery available?",
    "What cards do you accept?",
    "My item came broken",
]

for question in faq_edge:
    result = find_best_answer(question, kb)
    print(f"Q: {question}")
    print(f"   Found: {result['found']}")
    print(f"   Score: {result['confidence_score']}")
    print(f"   Matched: {result['matched_question']}")
    print()