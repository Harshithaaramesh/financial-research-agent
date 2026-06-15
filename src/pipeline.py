"""
pipeline.py
-----------
Single reusable function that runs the full research pipeline for one ticker.
Both the Research tab and Comparison tab call this — no duplicated logic.

Returns a PipelineResult dict so callers can render status however they like.
"""

from pathlib import Path


def run_pipeline(
    ticker: str,
    company_name: str,
    status_cb=None,
) -> dict:
    """
    Run the full ingestion → RAG → multi-agent pipeline for one company.

    Args:
        ticker:       Validated, uppercase stock ticker, e.g. 'JPM'
        company_name: Sanitised company name, e.g. 'JPMorgan Chase'
        status_cb:    Optional callable(message: str) for progress updates.
                      Pass st.write in Streamlit, or print in CLI.

    Returns a dict with keys:
        final_report  str   — Markdown investment memo
        filing_len    int   — Characters in 10-K filing
        news_len      int   — Characters in news corpus
        chunks        int   — Number of RAG chunks created
        context_len   int   — Characters of retrieved context
        error         str | None  — Set if the pipeline failed
    """
    log = status_cb or (lambda msg: None)

    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/vectorstore").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)

    try:
        # Phase 1: Ingestion 
        log(f"📥 Fetching 10-K SEC filing for **{ticker}**...")
        from src.ingestion.edgar_fetcher import get_10k_text
        filing_text = get_10k_text(ticker, save_to=f"data/raw/{ticker}_10k.txt")

        if not filing_text:
            return {
                "final_report": None,
                "error": f"No 10-K filing found for **{ticker}**. Check the ticker symbol.",
            }
        log(f"✅ 10-K: {len(filing_text):,} chars")

        from src.ingestion.news_fetcher import get_news_text
        news_text = get_news_text(company_name, save_to=f"data/raw/{ticker}_news.txt")
        log(f"✅ News: {len(news_text):,} chars")

        # Phase 2: RAG 
        log("📚 Building vector index...")
        from src.rag.chunker import chunk_documents
        from src.rag.embedder import build_vectorstore
        from src.rag.retriever import retrieve_multi

        all_text    = filing_text + "\n\n" + news_text
        chunks      = chunk_documents(all_text)
        log(f"✅ {len(chunks):,} chunks created")

        vectorstore = build_vectorstore(
            chunks,
            save_path=f"data/vectorstore/{ticker}",
        )
        context = retrieve_multi(
            vectorstore=vectorstore,
            queries=[
                "revenue profit earnings growth financial performance",
                "risks lawsuits regulatory investigations legal",
                "news sentiment analyst outlook market perception",
            ],
            k=3,   # 3 queries × 3 chunks ≈ 9 unique chunks; keeps input tokens lean
        )
        log(f"✅ Retrieved {len(context):,} chars of context")

        # Phase 3: Agents 
        log("🤖 Running AI agents (Fundamentals · Risk · Sentiment · Coordinator)...")
        from src.agents.graph import build_graph
        graph  = build_graph()
        result = graph.invoke({
            "company":       company_name,
            "context":       context,
            "fundamentals":  "",
            "risk":          "",
            "sentiment":     "",
            "final_report":  "",
        })
        log("✅ Analysis complete")

        return {
            "final_report": result["final_report"],
            "filing_len":   len(filing_text),
            "news_len":     len(news_text),
            "chunks":       len(chunks),
            "context_len":  len(context),
            "error":        None,
        }

    except Exception as exc:
        return {"final_report": None, "error": str(exc)}
