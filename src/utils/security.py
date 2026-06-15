"""
security.py
-----------
Two lightweight security controls wired into the Streamlit app:

  1. Input validation  — ensures the ticker is safe before it touches the
                         filesystem or external APIs.
  2. Rate limiting     — prevents a single session from hammering Groq /
                         EDGAR on every keystroke.  Uses Streamlit session
                         state so no external Redis / database is needed.

Why these two first?
  - Ticker validation closes a real path-traversal hole: without it a user
    could enter '../../etc/passwd' and corrupt the data/ directory.
  - Rate limiting protects your free-tier Groq quota and EDGAR's fair-use
    policy, both of which would silently break the app if exceeded.
"""

import re
import time
import streamlit as st

# Constants 
TICKER_PATTERN   = re.compile(r"^[A-Z0-9]{1,6}$")   # NYSE/NASDAQ max 5, some 6
MAX_REQUESTS     = 5          # max pipeline runs per window
WINDOW_SECONDS   = 600        # 10-minute rolling window
SESSION_KEY      = "_rate_limit_timestamps"


# 1. Input Validation 

class ValidationError(ValueError):
    """Raised when user input fails a security check."""


def validate_ticker(raw: str, allow_empty: bool = False) -> str:
    """
    Sanitise and validate a stock ticker symbol.

    Rules
    -----
    - Strip whitespace, convert to uppercase
    - Must match ^[A-Z0-9]{1,6}$  (letters and digits only, 1-6 chars)
    - If allow_empty=True, returns '' without error (used when ticker is optional)

    Returns the cleaned ticker string.
    Raises ValidationError with a user-friendly message on failure.
    """
    cleaned = raw.strip().upper()

    if not cleaned:
        if allow_empty:
            return ""
        raise ValidationError("Ticker cannot be empty.")

    if len(cleaned) > 6:
        raise ValidationError(
            f"'{cleaned}' is too long to be a valid ticker (max 6 characters). "
            "Enter the stock symbol, e.g. AAPL, JPM, MSFT."
        )

    if not TICKER_PATTERN.match(cleaned):
        raise ValidationError(
            f"'{cleaned}' contains invalid characters. "
            "Tickers must contain only letters and numbers, e.g. AAPL, JPM, BRK-B."
        )

    return cleaned


def validate_company_name(raw: str, allow_empty: bool = False) -> str:
    """
    Basic sanitisation for the company name field.

    - Strip leading/trailing whitespace
    - Cap length at 120 chars (prevents oversized prompts)
    - Strip characters that could break HTML/prompt injection
    - If allow_empty=True, returns '' without error (used when company is optional)

    Returns the cleaned name.
    Raises ValidationError on failure.
    """
    cleaned = raw.strip()

    if not cleaned:
        if allow_empty:
            return ""
        raise ValidationError("Company name cannot be empty.")

    if len(cleaned) > 120:
        raise ValidationError("Company name is too long (max 120 characters).")

    # Remove anything that isn't a letter, digit, space, or common punctuation
    sanitised = re.sub(r"[^\w\s\-\.,&'()]", "", cleaned)

    if not sanitised:
        raise ValidationError("Company name contains no valid characters.")

    return sanitised


def validate_email(raw: str) -> str:
    """
    Lightweight email format check (not full RFC 5322 — that's overkill here).
    Returns cleaned email or raises ValidationError.
    """
    cleaned = raw.strip().lower()
    pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    if not pattern.match(cleaned):
        raise ValidationError(f"'{raw}' doesn't look like a valid email address.")
    return cleaned


# 2. Rate Limiting 

class RateLimitError(Exception):
    """Raised when the session has exceeded the allowed request rate."""


def _get_timestamps() -> list[float]:
    """Return the list of request timestamps stored in session state."""
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = []
    return st.session_state[SESSION_KEY]


def _prune_old(timestamps: list[float], now: float) -> list[float]:
    """Remove timestamps outside the rolling window."""
    cutoff = now - WINDOW_SECONDS
    return [t for t in timestamps if t > cutoff]


def check_rate_limit() -> None:
    """
    Check whether this Streamlit session is within the rate limit.

    Raises RateLimitError with a user-friendly message if the limit is hit.
    Must be called BEFORE starting the pipeline so we don't waste resources.
    """
    now = time.time()
    timestamps = _prune_old(_get_timestamps(), now)

    if len(timestamps) >= MAX_REQUESTS:
        oldest = timestamps[0]
        wait_secs = int(WINDOW_SECONDS - (now - oldest)) + 1
        wait_mins = max(1, wait_secs // 60)
        raise RateLimitError(
            f"You've run {MAX_REQUESTS} analyses in the last 10 minutes. "
            f"Please wait ~{wait_mins} minute(s) before trying again. "
            "This keeps the service fair for all users and protects API quotas."
        )

    # Record this request
    timestamps.append(now)
    st.session_state[SESSION_KEY] = timestamps


def remaining_requests() -> int:
    """
    Returns how many pipeline runs the current session can still make
    within the current window.  Useful to show in the UI.
    """
    now = time.time()
    timestamps = _prune_old(_get_timestamps(), now)
    return max(0, MAX_REQUESTS - len(timestamps))
