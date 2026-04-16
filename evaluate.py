import csv
from datetime import datetime
from utils import load_kb
from guardrails import should_escalate, is_tracking_question
from retrieval import find_best_answer


# -----------------------------
# Test cases
# -----------------------------

TEST_CASES = [
    # --- FAQ answer cases ---
    {"question": "What is your return policy?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "How long does shipping take?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "Do you ship internationally?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "Can I cancel my order?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "What if my item arrives damaged?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "How much does shipping cost?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "Do you offer free shipping?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "What payment methods do you accept?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "Do you send tracking numbers?", "expected_action": "answer", "category": "faq_answer"},
    {"question": "Can I place an order without creating an account?", "expected_action": "answer", "category": "faq_answer"},

    # --- FAQ edge cases ---
    {"question": "What are the returns like?", "expected_action": "answer", "category": "faq_edge"},
    {"question": "How fast is delivery?", "expected_action": "answer", "category": "faq_edge"},
    {"question": "Is international delivery available?", "expected_action": "answer", "category": "faq_edge"},
    {"question": "What cards do you accept?", "expected_action": "answer", "category": "faq_edge"},
    {"question": "My item came broken", "expected_action": "answer", "category": "faq_edge"},

    # --- Standard escalation cases ---
    {"question": "Give me a refund now", "expected_action": "escalate", "category": "guardrail"},
    {"question": "Change my address", "expected_action": "escalate", "category": "guardrail"},
    {"question": "I want compensation", "expected_action": "escalate", "category": "guardrail"},
    {"question": "Cancel payment now", "expected_action": "escalate", "category": "guardrail"},
    {"question": "I want to sue the company", "expected_action": "escalate", "category": "guardrail"},
    {"question": "Make an exception to your policy", "expected_action": "escalate", "category": "guardrail"},

    # --- Regex variation escalation cases ---
    {"question": "I need a refund for my order", "expected_action": "escalate", "category": "guardrail_regex"},
    {"question": "Please change my delivery address", "expected_action": "escalate", "category": "guardrail_regex"},
    {"question": "I want to speak to a manager", "expected_action": "escalate", "category": "guardrail_regex"},
    {"question": "This is clearly fraud", "expected_action": "escalate", "category": "guardrail_regex"},
    {"question": "I will file a lawsuit", "expected_action": "escalate", "category": "guardrail_regex"},

    # --- Anger detection cases ---
    {"question": "This is completely unacceptable", "expected_action": "escalate", "category": "anger"},
    {"question": "Your service is absolutely terrible", "expected_action": "escalate", "category": "anger"},
    {"question": "This is a total scam", "expected_action": "escalate", "category": "anger"},
    {"question": "I am so furious right now", "expected_action": "escalate", "category": "anger"},
    {"question": "I am frustrated with this service", "expected_action": "escalate", "category": "anger"},

    # --- Fallback cases ---
    {"question": "Tell me about warranty extensions", "expected_action": "fallback", "category": "fallback"},
    {"question": "Do you offer gift wrapping?", "expected_action": "fallback", "category": "fallback"},
    {"question": "Can I subscribe for monthly deliveries?", "expected_action": "fallback", "category": "fallback"},
    {"question": "Do you sell insurance plans?", "expected_action": "fallback", "category": "fallback"},
    {"question": "Can I schedule delivery for next month?", "expected_action": "fallback", "category": "fallback"},
]


# -----------------------------
# Evaluation logic
# -----------------------------

def evaluate_case(question: str, kb: list) -> dict:
    escalate, reason = should_escalate(question)
    if escalate:
        return {"action": "escalate", "reason": reason, "answer": None, "source": None, "confidence_score": None}

    result = find_best_answer(question, kb)
    if result["found"]:
        return {"action": "answer", "reason": None, "answer": result["answer"], "source": result["source"], "confidence_score": result["confidence_score"]}

    return {"action": "fallback", "reason": None, "answer": None, "source": None, "confidence_score": result["confidence_score"]}


def print_category_summary(category: str, total: int, passed: int):
    accuracy = (passed / total * 100) if total > 0 else 0
    print(f"{category}: {passed}/{total} passed ({accuracy:.2f}%)")


# -----------------------------
# Report export
# -----------------------------

def save_report(results: list):
    filename = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    headers = ["test_number", "category", "question", "expected", "actual", "passed", "confidence_score", "reason", "source"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nReport saved to: {filename}")


# -----------------------------
# Main
# -----------------------------

def main():
    kb = load_kb()

    total = len(TEST_CASES)
    passed = 0
    category_totals = {}
    category_passed = {}
    report_rows = []

    print("Running evaluation...\n")

    for index, case in enumerate(TEST_CASES, start=1):
        question = case["question"]
        expected = case["expected_action"]
        category = case["category"]

        category_totals[category] = category_totals.get(category, 0) + 1

        actual = evaluate_case(question, kb)
        actual_action = actual["action"]
        is_pass = actual_action == expected

        if is_pass:
            passed += 1
            category_passed[category] = category_passed.get(category, 0) + 1
        else:
            category_passed.setdefault(category, 0)

        print(f"Test {index} | {category}")
        print(f"Q: {question}")
        print(f"Expected: {expected} | Actual: {actual_action} | Pass: {is_pass}")
        if actual["confidence_score"] is not None:
            print(f"Confidence: {actual['confidence_score']}")
        print("-" * 50)

        report_rows.append({
            "test_number": index,
            "category": category,
            "question": question,
            "expected": expected,
            "actual": actual_action,
            "passed": is_pass,
            "confidence_score": actual["confidence_score"] or "",
            "reason": actual["reason"] or "",
            "source": actual["source"] or "",
        })

    # Summary
    print(f"\nEvaluation summary")
    print("=" * 50)
    print(f"Passed {passed}/{total} tests")
    print(f"Overall accuracy: {passed / total * 100:.2f}%\n")

    print("Category breakdown")
    print("=" * 50)
    for category in sorted(category_totals.keys()):
        print_category_summary(category, category_totals[category], category_passed.get(category, 0))

    save_report(report_rows)


if __name__ == "__main__":
    main()