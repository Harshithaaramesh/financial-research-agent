"""
main.py
-------
Entry point for testing the full pipeline from terminal.
Run this to verify each phase works before launching the UI.

Usage:
    python main.py
"""

from pathlib import Path

# Create required folders if they don't exist 
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/vectorstore").mkdir(parents=True, exist_ok=True)
Path("outputs/reports").mkdir(parents=True, exist_ok=True)

# Config — change these to test different companies 
TICKER = "JPM"                  # Stock ticker
COMPANY_NAME = "JPMorgan Chase" # Full company name (used for news search)

print("\n" + "=" * 65)
print(f"  Financial Research Agent — Testing pipeline for: {COMPANY_NAME}")
print("=" * 65)


# PHASE 2 — Data Ingestion

print("\n📥 PHASE 2: Fetching Documents...")

from src.ingestion.edgar_fetcher import get_10k_text
from src.ingestion.news_fetcher import get_news_text

filing_text = get_10k_text(
    ticker=TICKER,
    save_to=f"data/raw/{TICKER}_10k.txt"
)
news_text = get_news_text(
    company_name=COMPANY_NAME,
    save_to=f"data/raw/{TICKER}_news.txt"
)

if not filing_text:
    raise RuntimeError("Failed to fetch 10-K filing. Check ticker and internet connection.")

print(f"Phase 2 done. 10-K: {len(filing_text):,} chars | News: {len(news_text):,} chars")


# PHASE 3 — RAG Pipeline
print("\n📚 PHASE 3: Building RAG Index...")

from src.rag.chunker import chunk_documents
from src.rag.embedder import build_vectorstore
from src.rag.retriever import retrieve_multi

# Combine filing + news into one document
all_text = filing_text + "\n\n" + news_text

# Split into chunks
chunks = chunk_documents(all_text)

# Embed and store in FAISS
vectorstore = build_vectorstore(chunks, save_path="data/vectorstore")

# Retrieve context relevant to all three agent topics
context = retrieve_multi(
    vectorstore=vectorstore,
    queries=[
        "revenue profit earnings growth financial performance",
        "risks lawsuits regulatory investigations legal",
        "news sentiment analyst outlook market perception",
    ],
    k=5,
)

print(f"Phase 3 done. Context: {len(context):,} chars retrieved.")


# PHASE 4 & 5 — Agents + LangGraph Orchestration
print("\n🤖 PHASE 4 & 5: Running Multi-Agent Pipeline...")

from src.agents.graph import build_graph

graph = build_graph()

result = graph.invoke({
    "company": COMPANY_NAME,
    "context": context,
    "fundamentals": "",
    "risk": "",
    "sentiment": "",
    "final_report": "",
})

final_report = result["final_report"]


# Output
print("\n" + "=" * 65)
print("  FINAL INVESTMENT MEMO")
print("=" * 65)
print(final_report)

# Save the report
report_path = f"outputs/reports/{TICKER}_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(final_report)

print("\n" + "=" * 65)
print(f"Report saved to: {report_path}")
print("=" * 65)
