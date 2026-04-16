APP_TITLE = "Customer Support AI Assistant"
APP_ICON = "💬"

# -----------------------------
# Escalation
# -----------------------------

ESCALATION_KEYWORDS = [
    "refund",
    "compensation",
    "legal",
    "fraud",
    "chargeback",
    "sue",
    "lawsuit",
    "cancel payment",
    "change my address",
    "change address",
    "exception",
    "complaint",
    "angry",
    "manager",
    "escalate",
]

# Regex patterns for flexible escalation matching
ESCALATION_PATTERNS = [
    r"\brefund\b",
    r"\bcompensation\b",
    r"\blegal\b",
    r"\bfraud\b",
    r"\bchargeback\b",
    r"\bsue\b",
    r"\blawsuit\b",
    r"\bcancel\s+payment\b",
    r"\bchange\s+(my\s+)?(\w+\s+)?address\b",
    r"\bexception\b",
    r"\bcomplaint\b",
    r"\bmanager\b",
    r"\bescalate\b",
    
]

# Anger/frustration signals
ANGER_PATTERNS = [
    r"\bunacceptable\b",
    r"\bthis is ridiculous\b",
    r"\bterrible\b",
    r"\bworst\b",
    r"\bdisgusting\b",
    r"\bscam\b",
    r"\bhorrible\b",
    r"\bfrustrated\b",
    r"\bfurious\b",
    r"\boutraged\b",
    r"\bi am\s+(so\s+)?(angry|upset|frustrated|livid)\b",
]

# -----------------------------
# Tracking
# -----------------------------

TRACKING_KEYWORDS = [
    "where is my order",
    "track my order",
    "track order",
    "tracking",
    "order status",
    "where's my order",
]

TRACKING_PATTERNS = [
    r"\btrack(ing)?\b",
    r"\bwhere\s+is\s+my\s+order\b",
    r"\border\s+status\b",
    r"\bwhere.s\s+my\s+order\b",
]

# -----------------------------
# Retrieval
# -----------------------------

MIN_CONFIDENCE_SCORE = 3.2

# -----------------------------
# Messages
# -----------------------------

SAFE_FALLBACK_MESSAGE = (
    "I could not find a reliable answer in the knowledge base. "
    "Please escalate this case to a human agent."
)

ESCALATION_MESSAGE_TEMPLATE = (
    "This request has been escalated to a human agent because it contains "
    "a high-risk topic: '{reason}'."
)
# -----------------------------
# LLM
# -----------------------------

LLM_MODEL = "claude-sonnet-4-20250514"

LLM_SYSTEM_PROMPT = """
You are a customer support assistant for an e-commerce business.
You only answer questions related to:
- Shipping and delivery
- Returns and exchanges
- Order tracking
- Cancellations
- Damaged or incorrect items
- Payment methods
- General order questions

Rules:
- Never discuss refunds, compensation, legal matters, fraud, or policy exceptions. If asked, say a human agent will assist.
- Never make up specific policies. If unsure, say you cannot confirm and suggest contacting support.
- Keep answers short, clear, and professional.
- If the question is completely unrelated to e-commerce support, say you cannot help with that topic.
"""

LLM_FALLBACK_MESSAGE = (
    "I was unable to find a reliable answer. "
    "A human agent will follow up with you shortly."
)