"""
edgar_fetcher.py
----------------
Fetches the latest 10-K filing for a given company from the SEC EDGAR API.

How it works:
  1. Look up the company's CIK number (SEC's unique ID) using their stock ticker.
  2. Fetch the list of all filings from EDGAR.
  3. Find the most recent 10-K filing.
  4. Download and return the raw text of that filing.

SEC EDGAR is completely free — no API key needed.
"""

import requests
import re
import time

# EDGAR requires a User-Agent header and it's their policy.
# Update this with your own name and email.
HEADERS = {
    "User-Agent": "Harshitha Bengaluru Rameshbabu harshithabr182@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}


def get_cik_from_ticker(ticker: str) -> str | None:
    """
    Converts a stock ticker (e.g. 'AAPL') to a CIK number (e.g. '0000320193').
    SEC EDGAR identifies every company by a CIK, not a ticker.
    """
    print(f"  [EDGAR] Looking up CIK for ticker: {ticker.upper()}...")

    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    companies = response.json()
    ticker_upper = ticker.upper()

    for entry in companies.values():
        if entry["ticker"].upper() == ticker_upper:
            cik = str(entry["cik_str"]).zfill(10)  # zero-pad to 10 digits
            print(f"  [EDGAR] Found CIK: {cik} → {entry['title']}")
            return cik

    print(f"  [EDGAR] Could not find CIK for ticker '{ticker}'.")
    return None


def get_latest_10k_url(cik: str) -> tuple[str, str] | tuple[None, None]:
    """
    Given a CIK, returns the URL of the company's most recent 10-K filing.
    """
    print(f"  [EDGAR] Fetching filing list...")

    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    filings = data.get("filings", {}).get("recent", {})

    forms = filings.get("form", [])
    accession_numbers = filings.get("accessionNumber", [])
    filing_dates = filings.get("filingDate", [])
    primary_documents = filings.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form == "10-K":
            accession = accession_numbers[i].replace("-", "")
            date = filing_dates[i]
            primary_doc = primary_documents[i]
            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/{accession}/{primary_doc}"
            )
            print(f"  [EDGAR] Found 10-K filed on {date}")
            return filing_url, date

    print("  [EDGAR] No 10-K filing found.")
    return None, None


def fetch_filing_text(url: str) -> str:
    """
    Downloads the 10-K filing and returns plain text (strips HTML if needed).
    """
    print(f"  [EDGAR] Downloading filing...")
    time.sleep(0.5)  # Be polite — don't hammer EDGAR's servers

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    raw = response.text

    # Strip HTML tags if the document is HTML
    if "<html" in raw.lower():
        raw = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
        raw = re.sub(r"<style[^>]*>.*?</style>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
        raw = re.sub(r"<[^>]+>", " ", raw)
        raw = re.sub(r"\s{3,}", "\n\n", raw)

    text = raw.strip()
    print(f"  [EDGAR] Downloaded {len(text):,} characters.")
    return text


def get_10k_text(ticker: str, save_to: str | None = None) -> str | None:
    """
    Main function: given a stock ticker, returns the full text of the
    company's latest 10-K SEC filing.

    Args:
        ticker:   Stock ticker, e.g. 'JPM', 'AAPL', 'MSFT'
        save_to:  Optional path to save raw text, e.g. 'data/raw/JPM_10k.txt'

    Returns:
        The filing as a plain-text string, or None on failure.
    """
    print(f"\n[EDGAR] Fetching 10-K for '{ticker.upper()}'...")

    cik = get_cik_from_ticker(ticker)
    if not cik:
        return None

    filing_url, filing_date = get_latest_10k_url(cik)
    if not filing_url:
        return None

    text = fetch_filing_text(filing_url)

    if save_to:
        with open(save_to, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  [EDGAR] Saved to: {save_to}")

    print(f"[EDGAR] Done. Filing date: {filing_date}\n")
    return text
