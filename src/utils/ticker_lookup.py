"""
ticker_lookup.py
----------------
Auto-detect ticker from company name (or company name from ticker)
using SEC EDGAR's free public company directory — no API key needed.

SEC publishes a full list of ~10k public companies at:
  https://www.sec.gov/files/company_tickers.json

We load it once per session (cached in memory), then do a fuzzy
name match to return the best ticker + official company name.
"""

import re
import json
import time
import requests
from functools import lru_cache

EDGAR_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_CACHE_TTL = 3600          # re-fetch at most once per hour
_last_fetch: float = 0
_company_list: list[dict] = []


def _fetch_company_list() -> list[dict]:
    """
    Download SEC EDGAR's public company list and cache it in memory.
    Returns a list of dicts: [{ticker, name, cik}, ...]
    """
    global _last_fetch, _company_list
    now = time.time()
    if _company_list and (now - _last_fetch) < _CACHE_TTL:
        return _company_list

    try:
        resp = requests.get(
            EDGAR_TICKERS_URL,
            headers={"User-Agent": "financial-research-assistant contact@example.com"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()                       # {0: {cik_str, ticker, title}, ...}
        _company_list = [
            {
                "ticker": v["ticker"].upper(),
                "name":   v["title"],
                "cik":    v["cik_str"],
            }
            for v in data.values()
        ]
        _last_fetch = now
    except Exception:
        pass   # silently return whatever we have (or empty list)

    return _company_list


def _normalise(text: str) -> str:
    """Lowercase, strip common suffixes, collapse spaces."""
    t = text.lower()
    # Remove common corporate suffixes for better matching
    for suffix in [
        r"\binc\.?$", r"\bcorp\.?$", r"\bltd\.?$", r"\bco\.?$",
        r"\bllc\.?$", r"\bplc\.?$", r"\bgroup$", r"\bholdings?$",
    ]:
        t = re.sub(suffix, "", t, flags=re.IGNORECASE).strip()
    return re.sub(r"\s+", " ", t).strip()


def lookup_ticker(company_name: str) -> tuple[str, str] | tuple[None, None]:
    """
    Given a company name, return (ticker, official_name) or (None, None).

    Matching strategy:
      1. Exact normalised-name match  (highest confidence)
      2. Name starts-with match       (e.g. "JPMorgan" → "JPMORGAN CHASE & CO")
      3. Contains match on every word (e.g. "Goldman" → "GOLDMAN SACHS GROUP")
    """
    companies = _fetch_company_list()
    if not companies:
        return None, None

    needle = _normalise(company_name)
    if not needle:
        return None, None

    # Pass 1 — exact normalised match
    for c in companies:
        if _normalise(c["name"]) == needle:
            return c["ticker"], c["name"]

    # Pass 2 — name starts with the query
    for c in companies:
        if _normalise(c["name"]).startswith(needle):
            return c["ticker"], c["name"]

    # Pass 3 — all words in query appear in the company name
    words = needle.split()
    for c in companies:
        norm = _normalise(c["name"])
        if all(w in norm for w in words):
            return c["ticker"], c["name"]

    return None, None


def lookup_company(ticker: str) -> str | None:
    """
    Given a ticker, return the official company name from SEC EDGAR.
    Returns None if not found.
    """
    companies = _fetch_company_list()
    ticker_up = ticker.upper()
    for c in companies:
        if c["ticker"] == ticker_up:
            return c["name"].title()   # title-case is more readable
    return None
