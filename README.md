# 📊 Financial Research Assistant

> A multi-agent AI system that automates equity research — fetching SEC filings, running specialist AI analysts, and generating a professional investment memo in under 2 minutes.

Built with LangChain · LangGraph · FAISS · Groq · SEC EDGAR · Streamlit

---

## What It Does

Equity analysts spend 2–4 hours on every new company doing the same things: finding the 10-K, reading the risk section, scanning news, and writing a first-draft memo. This system automates that entire workflow:

1. Fetches the latest 10-K filing from SEC EDGAR (free, no API key)
2. Pulls recent news headlines via NewsAPI
3. Indexes everything with RAG (chunking → embeddings → FAISS vector search)
4. Runs three specialist AI agents in parallel (fundamentals, risk, sentiment)
5. A coordinator agent synthesises them into a professional investment memo
6. Exports to PDF and emails it — all from a clean web UI

---

## Architecture

```
User Input (company name / ticker)
        │
        ▼
┌─────────────────────────────────────┐
│           Data Ingestion            │
│  SEC EDGAR 10-K  ·  NewsAPI News    │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│           RAG Pipeline              │
│  Chunker → HuggingFace Embeddings   │
│         → FAISS Vector Store        │
│         → Semantic Retrieval        │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│       LangGraph Multi-Agent         │
│                                     │
│  ┌────────────┐  ┌───────────────┐  │
│  │Fundamentals│  │  Risk Agent   │  │
│  │   Agent    │  │               │  │
│  └─────┬──────┘  └──────┬────────┘  │
│        │                │           │
│        │   ┌──────────┐ │           │
│        └──►│Coordinator◄┘           │
│            │  Agent   │             │
│        ┌──►│          │             │
│        │   └────┬─────┘             │
│  ┌─────┴──────┐ │                   │
│  │ Sentiment  │ │                   │
│  │   Agent    │ │                   │
│  └────────────┘ │                   │
└─────────────────┼───────────────────┘
                  │
                  ▼
         Investment Memo (Markdown)
                  │
          ┌───────┴────────┐
          │                │
        PDF Export     Email Delivery
        (ReportLab)   (Gmail SMTP)
```

---

## Features

- **Auto-detect ticker** — enter only a company name; the system queries SEC EDGAR's public directory (~10k companies) and finds the ticker automatically
- **Multi-model fallback** — if Groq rate-limits one model, automatically retries with the next (llama-3.3-70b → llama-3.1-8b → gemma2-9b)
- **RAG over SEC filings** — 10-K files can exceed 1M characters; only the 9 most relevant chunks are sent to each agent
- **PDF generation** — professional report with cover page, section headers, and page footers via ReportLab
- **Email delivery** — sends the PDF as an attachment via Gmail SMTP (no third-party service)
- **Report history** — all memos stored in SQLite; view, re-download, or delete past reports
- **Company comparison** — analyse two companies side-by-side with dual progress displays
- **Authentication** — login system with bcrypt-hashed passwords and two roles: `admin` and `analyst`
- **Rate limiting** — 5 pipeline runs per 10 minutes per session
- **Audit logging** — every action (login, report generated, email sent, deletion) is logged with timestamp and username

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Agent orchestration | LangGraph (StateGraph) |
| LLM framework | LangChain |
| LLM inference | Groq API (Llama 3.3 70B, Llama 3.1 8B, Gemma 2 9B) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` (local, free) |
| Vector search | FAISS |
| Financial data | SEC EDGAR public API (free, no key) |
| News | NewsAPI free tier |
| PDF generation | ReportLab Platypus |
| Database | SQLite (stdlib) |
| Email | Gmail SMTP SSL (stdlib `smtplib`) |
| Auth | streamlit-authenticator + bcrypt |

**Total cost to run: $0** — every component uses a free tier or open-source library.

---

## Project Structure

```
financial-research-agent/
├── app.py                      # Streamlit UI — all tabs, auth, progress display
├── main.py                     # CLI entry point (for testing pipeline directly)
├── requirements.txt
├── config/
│   └── auth.yaml               # User credentials (NOT committed — see .gitignore)
├── src/
│   ├── pipeline.py             # Orchestrates ingestion → RAG → agents → output
│   ├── agents/
│   │   ├── graph.py            # LangGraph StateGraph definition
│   │   ├── fundamentals_agent.py
│   │   ├── risk_agent.py
│   │   ├── sentiment_agent.py
│   │   └── coordinator_agent.py
│   ├── ingestion/
│   │   ├── edgar_fetcher.py    # SEC EDGAR 10-K downloader
│   │   └── news_fetcher.py     # NewsAPI article fetcher
│   ├── rag/
│   │   ├── chunker.py          # RecursiveCharacterTextSplitter
│   │   ├── embedder.py         # HuggingFace embeddings + FAISS index
│   │   └── retriever.py        # Semantic retrieval (top-k chunks)
│   └── utils/
│       ├── llm.py              # invoke_with_fallback() — Groq multi-model chain
│       ├── security.py         # Input validation, rate limiting
│       ├── ticker_lookup.py    # SEC EDGAR company directory + fuzzy matching
│       ├── report_store.py     # SQLite persistence + audit logging
│       ├── pdf_generator.py    # ReportLab PDF builder
│       └── email_sender.py     # Gmail SMTP delivery
└── data/                       # Runtime data — NOT committed
    ├── raw/                    # Downloaded 10-K text files
    ├── vectorstore/            # FAISS indexes
    └── reports/                # Generated PDFs
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/<your-username>/financial-research-agent.git
cd financial-research-agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create a `.env` file

```env
GROQ_API_KEY=your_groq_api_key_here
NEWS_API_KEY=your_newsapi_key_here
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
```

Get your keys:
- **Groq** (free): https://console.groq.com
- **NewsAPI** (free): https://newsapi.org
- **Gmail app password**: Google Account → Security → 2-Step Verification → App passwords

### 3. Create the auth config

Copy the template and set up your credentials:

```bash
cp config/auth.yaml.example config/auth.yaml
```

Edit `config/auth.yaml` with your desired usernames and bcrypt-hashed passwords. The app uses `streamlit-authenticator` — passwords must be hashed with bcrypt before adding them to the file.

### 4. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Usage

1. **Log in** with your credentials
2. Go to the **Research** tab
3. Enter a company name (ticker is optional — auto-detected from SEC EDGAR)
4. Click **Run Analysis**
5. Watch the progress bar as the pipeline runs (~60–90 seconds)
6. View the investment memo, download the PDF, or email it directly

### Demo credentials (development only)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Analyst | `analyst` | `analyst123` |

> ⚠️ Change these before deploying anywhere.

---

## How It Differs from JPMorgan's IndexGPT

JPMorgan's IndexGPT is a **portfolio construction** tool — it selects which securities belong in a thematic index. This project is an **analyst augmentation** tool — it automates the preliminary research that happens *before* any investment decision. They solve different layers of the same workflow.

JPMorgan's internal **LLM Suite** (deployed to ~50,000 employees) is closer in spirit to this project, but backed by Bloomberg terminals, proprietary deal data, and fine-tuned models. This project achieves the same architectural patterns using only free, public data.

---

## Groq Free Tier — Token Budget

The three-model fallback chain gives an effective daily budget of:

| Model | Tokens/day |
|---|---|
| `llama-3.3-70b-versatile` | 100,000 |
| `llama-3.1-8b-instant` | 500,000 |
| `gemma2-9b-it` | 250,000 |
| **Total** | **~850,000** |

Each pipeline run uses ~7,000–12,000 tokens depending on filing length.

---

## License

MIT
