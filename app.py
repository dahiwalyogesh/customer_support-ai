import streamlit as st
import pandas as pd
import plotly.express as px
from database import initialize_db, get_chat_history, get_escalations, get_customers, seed_customers, insert_feedback, get_feedback, get_feedback_stats

from config import (
    APP_TITLE,
    APP_ICON,
    SAFE_FALLBACK_MESSAGE,
    ESCALATION_MESSAGE_TEMPLATE,
)
from utils import load_kb, load_orders
from logger import initialize_log_files
from router import route_question


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)

# -----------------------------
# Data init
# -----------------------------
initialize_db()
initialize_log_files()
seed_customers()
kb = load_kb()
orders = load_orders()

# -----------------------------
# Session state
# -----------------------------
if "stats" not in st.session_state:
    st.session_state.stats = {
        "answered_kb": 0,
        "answered_order_lookup": 0,
        "escalated": 0,
        "fallback": 0,
    }
if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False
if "question_input" not in st.session_state:
    st.session_state.question_input = ""

if "order_input" not in st.session_state:
    st.session_state.order_input = ""

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

SAMPLE_QUESTIONS = [
    "What is your return policy?",
    "How long does shipping take?",
    "Where is my order?",
    "Do you ship internationally?",
    "What if my item arrives damaged?",
    "Give me a refund now",
]

SUPPORTED_TOPICS = [
    "Return policy", "Shipping times", "Order tracking",
    "Cancellation policy", "Damaged items", "International shipping",
]

ESCALATED_TOPICS = [
    "Refund requests", "Compensation", "Address changes",
    "Legal / fraud", "Policy exceptions",
]

# -----------------------------
# Helpers
# -----------------------------
def inject_css():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }
        .hero-card {
            padding: 1.2rem 1.25rem;
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(79,70,229,0.14), rgba(14,165,233,0.10));
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1rem;
        }
        .mini-pill {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-right: 0.45rem;
            margin-bottom: 0.35rem;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.04);
        }
        .result-good {
            padding: 1rem;
            border-radius: 16px;
            background: rgba(34,197,94,0.10);
            border: 1px solid rgba(34,197,94,0.25);
        }
        .result-warn {
            padding: 1rem;
            border-radius: 16px;
            background: rgba(245,158,11,0.10);
            border: 1px solid rgba(245,158,11,0.25);
        }
        .result-bad {
            padding: 1rem;
            border-radius: 16px;
            background: rgba(239,68,68,0.10);
            border: 1px solid rgba(239,68,68,0.25);
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 20px;
            border-radius: 18px;
        }
        .small-muted {
            color: rgba(250,250,250,0.72);
            font-size: 0.92rem;
        }
        .chat-bubble-user {
            background: rgba(79,70,229,0.15);
            border: 1px solid rgba(79,70,229,0.25);
            border-radius: 16px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
        }
        .chat-bubble-bot {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
        }
        [data-testid="stSidebar"] {
            min-width: 280px;
            max-width: 280px;
        }
        </style>
    """, unsafe_allow_html=True)


def set_sample_question(text: str):
    st.session_state.question_input = text


def render_pills(items):
    html = "".join([f"<span class='mini-pill'>{item}</span>" for item in items])
    st.markdown(html, unsafe_allow_html=True)


def increment_stat(key: str):
    if key in st.session_state.stats:
        st.session_state.stats[key] += 1


def render_metrics(items):
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items):
        with column:
            st.metric(label, value)


def routing_chart():
    stats_df = pd.DataFrame({
        "route": ["KB Answer", "Order Lookup", "Escalated", "Fallback"],
        "count": [
            st.session_state.stats["answered_kb"],
            st.session_state.stats["answered_order_lookup"],
            st.session_state.stats["escalated"],
            st.session_state.stats["fallback"],
        ],
    })
    fig = px.bar(stats_df, x="route", y="count", title="Session Routing Summary", text="count")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=45, b=10))
    return fig


def knowledge_chart():
    topic_counts = pd.DataFrame({
        "category": ["KB Entries", "Orders", "Escalation Topics"],
        "count": [len(kb), len(orders), 5],
    })
    fig = px.pie(topic_counts, names="category", values="count", hole=0.55, title="System Coverage Snapshot")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=45, b=10))
    return fig


def show_success_box(title: str, message: str):
    st.markdown(f'<div class="result-good"><h4 style="margin-top:0;">{title}</h4><p>{message}</p></div>', unsafe_allow_html=True)


def show_warning_box(title: str, message: str):
    st.markdown(f'<div class="result-warn"><h4 style="margin-top:0;">{title}</h4><p>{message}</p></div>', unsafe_allow_html=True)


def show_error_box(title: str, message: str):
    st.markdown(f'<div class="result-bad"><h4 style="margin-top:0;">{title}</h4><p>{message}</p></div>', unsafe_allow_html=True)


def render_conversation_history():
    if not st.session_state.conversation_history:
        st.caption("No conversation history yet.")
        return

    for entry in reversed(st.session_state.conversation_history):
        st.markdown(f'<div class="chat-bubble-user">🧑 {entry["question"]}</div>', unsafe_allow_html=True)
        route_icon = {"answered": "✅", "escalated": "🚨", "fallback": "⚠️",
                      "tracking_found": "📦", "tracking_not_found": "❓", "tracking_missing_id": "⚠️"}.get(entry["route"], "💬")
        st.markdown(f'<div class="chat-bubble-bot">{route_icon} {entry["message"]}</div>', unsafe_allow_html=True)


def render_kb_browser():
    st.subheader("Knowledge Base Browser")
    st.caption(f"{len(kb)} entries loaded from kb.json")

    search_term = st.text_input("Search KB", placeholder="e.g. return, shipping, cancel")

    filtered = kb
    if search_term.strip():
        term = search_term.lower()
        filtered = [
            e for e in kb
            if term in e["question"].lower()
            or term in e["answer"].lower()
            or any(term in k.lower() for k in e.get("keywords", []))
        ]

    st.caption(f"Showing {len(filtered)} of {len(kb)} entries")

    for entry in filtered:
        with st.expander(f"#{entry['id']} — {entry['question']}"):
            st.markdown(f"**Answer:** {entry['answer']}")
            st.markdown(f"**Source:** {entry['source']}")
            st.markdown(f"**Keywords:** {', '.join(entry.get('keywords', []))}")


def render_history_exports():
    st.subheader("History & Exports")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Chat History")
        chat_rows = get_chat_history(limit=100)
        if chat_rows:
            chat_df = pd.DataFrame(chat_rows)
            st.dataframe(chat_df, use_container_width=True)
            st.download_button(
                "Download chat_history.csv",
                chat_df.to_csv(index=False),
                file_name="chat_history.csv",
                mime="text/csv",
            )
        else:
            st.caption("No chat history yet.")

    with col2:
        st.markdown("#### Escalations")
        esc_rows = get_escalations(limit=100)
        if esc_rows:
            esc_df = pd.DataFrame(esc_rows)
            st.dataframe(esc_df, use_container_width=True)
            st.download_button(
                "Download escalations.csv",
                esc_df.to_csv(index=False),
                file_name="escalations.csv",
                mime="text/csv",
            )
        else:
            st.caption("No escalations yet.")

    st.markdown("---")
    st.markdown("#### Customers")
    customer_rows = get_customers(limit=100)
    if customer_rows:
        customer_df = pd.DataFrame(customer_rows)
        st.dataframe(customer_df, use_container_width=True)
        st.download_button(
            "Download customers.csv",
            customer_df.to_csv(index=False),
            file_name="customers.csv",
            mime="text/csv",
        )
    else:
        st.caption("No customers yet.")

    st.markdown("---")
    st.markdown("#### Feedback Summary")
    stats = get_feedback_stats()
    fb_col1, fb_col2 = st.columns(2)
    with fb_col1:
        st.metric("👍 Helpful", stats["thumbs_up"])
    with fb_col2:
        st.metric("👎 Not helpful", stats["thumbs_down"])

    st.markdown("#### Feedback Log")
    feedback_rows = get_feedback(limit=100)
    if feedback_rows:
        feedback_df = pd.DataFrame(feedback_rows)
        st.dataframe(feedback_df, use_container_width=True)
        st.download_button(
            "Download feedback.csv",
            feedback_df.to_csv(index=False),
            file_name="feedback.csv",
            mime="text/csv",
        )
    else:
        st.caption("No feedback yet.")
    

inject_css()

with st.sidebar:
    st.markdown("## Support Assistant")
    st.markdown("Low-risk e-commerce support automation using retrieval, guardrails, and escalation.")

    st.markdown("### Supported topics")
    render_pills(SUPPORTED_TOPICS)

    st.markdown("### Escalated topics")
    render_pills(ESCALATED_TOPICS)

    st.markdown("### Sample questions")
    for sample in SAMPLE_QUESTIONS:
        if st.button(sample, use_container_width=True):
            set_sample_question(sample)

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.stats = {
            "answered_kb": 0,
            "answered_order_lookup": 0,
            "escalated": 0,
            "fallback": 0,
        }

render_metrics([
    ("Knowledge Base Entries", len(kb)),
    ("Sample Orders", len(orders)),
    ("Guardrail Mode", "Enabled"),
    ("Confidence Threshold", "3.2"),
])

# -----------------------------
# Tabs
# -----------------------------
tab_assistant, tab_kb, tab_history = st.tabs(["💬 Assistant", "📚 Knowledge Base", "📊 History & Exports"])

# -----------------------------
# Tab 1: Assistant
# -----------------------------
with tab_assistant:
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        st.subheader("Ask the assistant")

        question = st.text_input(
            "Customer question",
            key="question_input",
            placeholder="Example: What is your return policy?",
        )
        order_id = st.text_input(
            "Order ID (only for tracking questions)",
            key="order_input",
            placeholder="Example: ORD1001",
        )
        submit = st.button("Submit question", type="primary", use_container_width=True)

        with st.expander("How routing works", expanded=False):
            st.markdown(
                "1. Check if the request is high risk\n"
                "2. Route risky requests to human support\n"
                "3. Detect order-tracking requests\n"
                "4. Search the knowledge base for low-risk questions\n"
                "5. Return an answer with metadata or use a safe fallback"
            )

        if submit:
            st.subheader("Result")

            if not question.strip():
                st.warning("Please enter a customer question.")
            else:
                result = route_question(question, order_id, kb, orders)
                route = result["route"]
                message = result["message"]
                meta = result["meta"]

                if route == "escalated":
                    show_error_box("Escalated to human agent", f"<strong>Reason:</strong> {meta['reason']}<br><br>{message}")
                    st.info("This assistant only handles low-risk support queries.")
                    increment_stat("escalated")

                elif route == "tracking_missing_id":
                    show_warning_box("Order ID needed", message)

                elif route == "tracking_found":
                    show_success_box("Tracking result found", message)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.caption(f"Source: {meta['source']}")
                    with c2:
                        st.caption(f"Confidence: {meta['confidence']}")
                    increment_stat("answered_order_lookup")

                elif route == "tracking_not_found":
                    show_warning_box("Order not found", message)

                elif route == "answered":
                    show_success_box("Answer found", message)
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.caption(f"Source: {meta['source']}")
                    with c2:
                        st.caption(f"Confidence score: {meta['confidence_score']}")
                    with c3:
                        st.caption(f"Matched FAQ: {meta['matched_question']}")
                    increment_stat("answered_kb")
                elif route == "answered_llm":
                    show_success_box("Answer found (AI)", message)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.caption(f"Source: {meta['source']}")
                    with c2:
                        st.caption("Confidence: LLM generated")
                    increment_stat("answered_kb")

                elif route == "fallback":
                    show_warning_box("Fallback triggered", message)
                    increment_stat("fallback")

                # Add to conversation history
                st.session_state.conversation_history.append({
                    "question": question,
                    "route": route,
                    "message": message,
                })
                # Update last result for feedback
                st.session_state.last_result = {
                    "question": question,
                    "route": route,
                }
                st.session_state.feedback_given = False

        st.markdown("---")
        st.subheader("Conversation history")
        render_conversation_history()
        

        # -----------------------------
        # Feedback
        # -----------------------------
        if st.session_state.last_result and not st.session_state.feedback_given:
            st.markdown("---")
            st.markdown("**Was this answer helpful?**")
            fb_col1, fb_col2 = st.columns(2)

            with fb_col1:
                if st.button("👍 Yes, helpful", use_container_width=True):
                    insert_feedback(
                        st.session_state.last_result["question"],
                        st.session_state.last_result["route"],
                        "thumbs_up",
                    )
                    st.session_state.feedback_given = True
                    st.success("Thanks for your feedback!")

            with fb_col2:
                if st.button("👎 Not helpful", use_container_width=True):
                    insert_feedback(
                        st.session_state.last_result["question"],
                        st.session_state.last_result["route"],
                        "thumbs_down",
                    )
                    st.session_state.feedback_given = True
                    st.warning("Thanks — we'll use this to improve.")

        elif st.session_state.feedback_given:
            st.markdown("---")
            st.caption("✅ Feedback recorded for this answer.")

    with right_col:
        st.subheader("System snapshot")
        st.plotly_chart(knowledge_chart(), use_container_width=True)

        st.subheader("Live routing analytics")
        st.plotly_chart(routing_chart(), use_container_width=True)

        st.subheader("Prototype capabilities")
        st.markdown(
            "- FAQ retrieval from `kb.json`\n"
            "- Order lookup from `orders.csv`\n"
            "- Risk detection and escalation\n"
            "- Logging for traceability\n"
            "- Confidence-based fallback"
        )

# -----------------------------
# Tab 2: Knowledge Base
# -----------------------------
with tab_kb:
    render_kb_browser()

# -----------------------------
# Tab 3: History & Exports
# -----------------------------
with tab_history:
    render_history_exports()