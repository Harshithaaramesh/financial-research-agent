"""
news_fetcher.py
---------------
Fetches recent news headlines and summaries for a given company.

Two approaches (auto-selects best available):
  1. NewsAPI  — free at newsapi.org (100 req/day). Set NEWS_API_KEY in .env.
  2. Google News RSS — no API key needed. Used as fallback.
"""

import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"


def fetch_news_newsapi(company_name: str, days_back: int = 30) -> list[dict]:
    """
    Fetches articles via NewsAPI. Requires NEWS_API_KEY in .env.
    Returns a list of dicts with title, description, url, publishedAt, source.
    """
    if not NEWS_API_KEY or NEWS_API_KEY == "your_key_here":
        return []  # No key — fall back to RSS

    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "q": company_name,
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY,
    }

    print(f"  [NEWS] Fetching via NewsAPI for '{company_name}'...")
    response = requests.get(NEWS_API_URL, params=params)
    response.raise_for_status()

    articles = response.json().get("articles", [])
    print(f"  [NEWS] Found {len(articles)} articles via NewsAPI.")
    return [
        {
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "publishedAt": a.get("publishedAt", ""),
            "source": a.get("source", {}).get("name", ""),
        }
        for a in articles
    ]


def fetch_news_rss(company_name: str) -> list[dict]:
    """
    Fetches news via Google News RSS — no API key needed.
    Good for development/testing.
    """
    query = company_name.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    print(f"  [NEWS] Fetching via Google RSS for '{company_name}'...")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    channel = root.find("channel")

    results = []
    for item in channel.findall("item")[:20]:
        description = re.sub(r"<[^>]+>", "", item.findtext("description", ""))
        results.append({
            "title": item.findtext("title", ""),
            "description": description,
            "url": item.findtext("link", ""),
            "publishedAt": item.findtext("pubDate", ""),
            "source": "Google News",
        })

    print(f"  [NEWS] Found {len(results)} articles via RSS.")
    return results


def get_news_text(company_name: str, save_to: str | None = None) -> str:
    """
    Main function: returns all news for a company as a single plain-text string.
    Auto-uses NewsAPI if key is set in .env, otherwise falls back to RSS.

    Args:
        company_name: e.g. 'JPMorgan Chase', 'Apple'
        save_to:      Optional file path to save the text.

    Returns:
        Plain-text string of all articles concatenated.
    """
    print(f"\n[NEWS] Fetching news for '{company_name}'...")

    articles = fetch_news_newsapi(company_name) or fetch_news_rss(company_name)

    if not articles:
        print("  [NEWS] No articles found.")
        return ""

    lines = [f"=== RECENT NEWS: {company_name.upper()} ===\n"]
    for i, a in enumerate(articles, 1):
        lines.append(f"[Article {i}] {a['publishedAt']} | {a.get('source', '')}")
        lines.append(f"Title: {a['title']}")
        if a["description"]:
            lines.append(f"Summary: {a['description']}")
        lines.append("")

    text = "\n".join(lines)
    print(f"[NEWS] Done. {len(articles)} articles, {len(text):,} characters.\n")

    if save_to:
        with open(save_to, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  [NEWS] Saved to: {save_to}")

    return text
