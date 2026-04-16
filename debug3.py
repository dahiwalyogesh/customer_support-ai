# save as debug3.py and run: python debug3.py
from utils import load_kb
from guardrails import should_escalate
from retrieval import find_best_answer

kb = load_kb()

candidates = [
    # anger
    ("This is completely unacceptable", "escalate"),
    ("Your service is absolutely terrible", "escalate"),
    ("This is a total scam", "escalate"),
    ("I am so furious right now", "escalate"),
    ("I am frustrated with this service", "escalate"),
    # fallback
    ("Tell me about warranty extensions", "fallback"),
    ("Do you offer gift wrapping?", "fallback"),
    ("Can I subscribe for monthly deliveries?", "fallback"),
    ("Do you sell insurance plans?", "fallback"),
    ("Can I schedule delivery for next month?", "fallback"),
]

for question, expected in candidates:
    escalate, reason = should_escalate(question)
    action = "escalate" if escalate else None

    if not action:
        result = find_best_answer(question, kb)
        action = "answer" if result["found"] else "fallback"

    passed = action == expected
    if not passed:
        print(f"FAIL | Q: {question}")
        print(f"      Expected: {expected} | Actual: {action}")
        print()