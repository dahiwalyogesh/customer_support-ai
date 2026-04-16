from guardrails import should_escalate, is_tracking_question
from retrieval import find_best_answer, lookup_order_status
from logger import log_chat, log_escalation
from config import ESCALATION_MESSAGE_TEMPLATE, SAFE_FALLBACK_MESSAGE


def route_question(question: str, order_id: str, kb: list, orders: list) -> dict:
    """
    Routes a customer question through the support pipeline.

    Returns a result dict with keys:
        - route: "escalated" | "tracking_missing_id" | "tracking_found" |
                 "tracking_not_found" | "answered" | "fallback"
        - message: str
        - meta: dict (optional metadata for display)
    """

    # Step 1: Check for high-risk content
    escalate, reason = should_escalate(question)
    if escalate:
        message = ESCALATION_MESSAGE_TEMPLATE.format(reason=reason)
        log_escalation(question, reason)
        log_chat(question, action="escalated", answer="", source="", confidence_score="")
        return {
            "route": "escalated",
            "message": message,
            "meta": {"reason": reason},
        }

    # Step 2: Check for order tracking
    if is_tracking_question(question):
        if not order_id.strip():
            log_chat(question, action="tracking_missing_order_id", answer="", source="", confidence_score="")
            return {
                "route": "tracking_missing_id",
                "message": "Please enter an order ID for tracking questions.",
                "meta": {},
            }

        order = lookup_order_status(order_id, orders)
        if order:
            message = (
                f"Order <b>{order['order_id']}</b> for <b>{order['customer_name']}</b> "
                f"is currently <b>{order['status']}</b> and is expected on "
                f"<b>{order['estimated_delivery']}</b>."
            )
            log_chat(question, action="answered_order_lookup", answer=message, source="orders.csv", confidence_score="N/A")
            return {
                "route": "tracking_found",
                "message": message,
                "meta": {"source": "orders.csv", "confidence": "direct lookup"},
            }
        else:
            log_chat(question, action="order_not_found", answer="Order ID not found", source="orders.csv", confidence_score="N/A")
            return {
                "route": "tracking_not_found",
                "message": "Order ID not found. Please check the ID or escalate to a human agent.",
                "meta": {},
            }

    # Step 3: Search the knowledge base
    result = find_best_answer(question, kb)
    if result["found"]:
        log_chat(question, action="answered_kb", answer=result["answer"], source=result["source"], confidence_score=result["confidence_score"])
        return {
            "route": "answered",
            "message": result["answer"],
            "meta": {
                "source": result["source"],
                "confidence_score": result["confidence_score"],
                "matched_question": result["matched_question"],
            },
        }

    # Step 4: KB fallback — try LLM before giving up
    from llm import get_llm_response
    llm_result = get_llm_response(question)

    if llm_result["answered"]:
        log_chat(question, action="answered_llm", answer=llm_result["answer"], source="llm", confidence_score="llm")
        return {
            "route": "answered_llm",
            "message": llm_result["answer"],
            "meta": {"source": "Claude API"},
        }

    # LLM responded but was uncertain — still show its message, it's more helpful than generic fallback
    if llm_result["source"] == "llm_uncertain":
        log_chat(question, action="llm_uncertain", answer=llm_result["answer"], source="llm", confidence_score="llm")
        return {
            "route": "answered_llm",
            "message": llm_result["answer"],
            "meta": {"source": "Claude API (uncertain)"},
        }

    # Full fallback — LLM unavailable or errored
    log_chat(question, action="fallback_no_reliable_answer", answer=SAFE_FALLBACK_MESSAGE, source="", confidence_score=result["confidence_score"])
    return {
        "route": "fallback",
        "message": SAFE_FALLBACK_MESSAGE,
        "meta": {"confidence_score": result["confidence_score"]},
    }