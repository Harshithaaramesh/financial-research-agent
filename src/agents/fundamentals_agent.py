from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import invoke_with_fallback

FUNDAMENTALS_PROMPT = ChatPromptTemplate.from_template("""
You are a financial analyst specializing in company fundamentals at a major investment bank.

Analyze the financial health of the company based ONLY on the context provided.
Do not make up numbers. If a metric isn't mentioned, say "not mentioned".

CONTEXT FROM SEC FILING AND NEWS:
{context}

Provide a structured analysis covering:
1. Revenue & Profit: Key figures and trends.
2. Growth: YoY comparisons and trajectory.
3. Key Metrics: EPS, margins, cash flow, ROE where available.
4. Financial Health: Overall assessment — strong or weak?

Be concise and factual. Use numbers where available.
""")


def run_fundamentals_agent(context: str) -> str:
    print("  [AGENT] Running Fundamentals Agent...")
    result = invoke_with_fallback(FUNDAMENTALS_PROMPT, {"context": context}, max_tokens=800)
    print("  [AGENT] Fundamentals Agent done.")
    return result
