import os
import anthropic
from config import LLM_MODEL, LLM_SYSTEM_PROMPT, LLM_FALLBACK_MESSAGE
import streamlit as st

def get_llm_response(question: str) -> dict:
    """
    Calls the Claude API with a strict e-commerce support system prompt.
    Returns a result dict with keys:
        - answered: bool
        - answer: str
        - source: str
    """
    
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "answered": False,
            "answer": LLM_FALLBACK_MESSAGE,
            "source": "llm_unavailable",
        }

    try:
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=300,
            system=LLM_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": question}
            ],
        )

        answer = response.content[0].text.strip()

        uncertainty_phrases = [
            "i cannot help",
            "i can't help",
            "human agent",
            "contact support",
            "i'm unable",
            "i am unable",
            "cannot confirm",
        ]
        if any(phrase in answer.lower() for phrase in uncertainty_phrases):
            return {
                "answered": False,
                "answer": answer,
                "source": "llm_uncertain",
            }

        return {
            "answered": True,
            "answer": answer,
            "source": "llm",
        }

    except Exception as e:
        return {
            "answered": False,
            "answer": LLM_FALLBACK_MESSAGE,
            "source": f"llm_error: {str(e)}",
        }