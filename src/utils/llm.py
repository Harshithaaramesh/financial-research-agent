"""
llm.py
------
LLM configuration with automatic model fallback for Groq free tier.

Model fallback chain (each has an independent daily quota):
  1. llama-3.3-70b-versatile  — 100k TPD  (best quality)
  2. llama-3.1-8b-instant     — 500k TPD  (fast, separate quota)
  3. gemma2-9b-it             — 250k TPD  (Google Gemma, separate quota)

invoke_with_fallback() is the main entry point for all agents.
It retries the ACTUAL inference call across models on 429, so
it handles rate limits that only surface under real token load.
"""

import os
import time
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
log = logging.getLogger(__name__)

_MODEL_CHAIN = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]


def _make_llm(model: str, max_tokens: int, temperature: float = 0) -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError(
            "GROQ_API_KEY not set. Sign up free at https://console.groq.com "
            "and add GROQ_API_KEY=gsk_... to your .env file."
        )
    return ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        groq_api_key=api_key,
    )


def get_llm(model: str = "llama-3.3-70b-versatile", temperature: float = 0,
            max_tokens: int = 1024) -> ChatGroq:
    """Simple LLM factory — no fallback. Use invoke_with_fallback() in agents."""
    return _make_llm(model, max_tokens, temperature)


def invoke_with_fallback(prompt_template, input_dict: dict,
                         max_tokens: int = 800, temperature: float = 0) -> str:
    """
    Build a chain from prompt_template and invoke it with input_dict.
    Automatically retries with the next model in _MODEL_CHAIN on 429.

    Args:
        prompt_template: A LangChain ChatPromptTemplate
        input_dict:      The dict passed to chain.invoke()
        max_tokens:      Cap on output tokens (conserves daily quota)
        temperature:     0 = deterministic

    Returns:
        The model's response as a string.

    Raises:
        RuntimeError if every model in the chain is rate-limited.
    """
    last_error = None
    for model_name in _MODEL_CHAIN:
        try:
            llm   = _make_llm(model_name, max_tokens, temperature)
            chain = prompt_template | llm
            log.info(f"[LLM] Invoking {model_name}")
            result = chain.invoke(input_dict)
            return result.content
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit_exceeded" in err.lower():
                log.warning(f"[LLM] {model_name} rate-limited → trying next model")
                last_error = e
                time.sleep(0.5)
                continue
            raise   # non-429 errors propagate immediately

    raise RuntimeError(
        "All Groq models are currently rate-limited (free tier resets daily). "
        f"Last error: {last_error}\n\n"
        "Tip: wait ~15 minutes or upgrade to Groq Dev Tier at "
        "https://console.groq.com/settings/billing"
    )
