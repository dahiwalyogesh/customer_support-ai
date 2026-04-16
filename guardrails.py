import re
from config import (
    ESCALATION_PATTERNS,
    ANGER_PATTERNS,
    TRACKING_PATTERNS,
)


def normalize_text(text: str) -> str:
    return text.lower().strip()


def match_patterns(text: str, patterns: list) -> tuple[bool, str | None]:
    """
    Checks text against a list of regex patterns.
    Returns (matched, matched_pattern) or (False, None).
    """
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return True, match.group()
    return False, None


def should_escalate(question: str) -> tuple[bool, str | None]:
    """
    Returns (True, reason) if the question should be escalated.
    Checks both high-risk topic patterns and anger/sentiment signals.
    """
    text = normalize_text(question)

    # Check high-risk topic patterns
    matched, reason = match_patterns(text, ESCALATION_PATTERNS)
    if matched:
        return True, reason

    # Check anger/sentiment signals
    matched, reason = match_patterns(text, ANGER_PATTERNS)
    if matched:
        return True, f"angry tone detected: '{reason}'"

    return False, None


def is_tracking_question(question: str) -> bool:
    """
    Returns True if the question is about order tracking.
    """
    text = normalize_text(question)
    matched, _ = match_patterns(text, TRACKING_PATTERNS)
    return matched