# save as debug2.py and run: python debug2.py
from utils import load_kb
from guardrails import should_escalate
from retrieval import find_best_answer

kb = load_kb()

failing_candidates = [
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
    # guardrail_regex
    ("I need a refund for my order", "escalate"),
    ("Please change my delivery address", "escalate"),
    ("I want to speak to a manager", "escalate"),
    ("This is clearly fraud", "escalate"),
    ("I will file a lawsuit", "escalate"),
]

print("Failing tests:\n")
for question, expected in failing_candidates:
    escalate, reason = should_escalate(question)
    action = "escalate" if escalate else None

    if not action:
        result = find_best_answer(question, kb)
        action = "answer" if result["found"] else "fallback"

    passed = action == expected
    if not passed:
        print(f"Q: {question}")
        print(f"   Expected: {expected} | Actual: {action}")
        if reason:
            print(f"   Reason: {reason}")
        print()