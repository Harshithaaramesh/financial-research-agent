from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import invoke_with_fallback

SENTIMENT_PROMPT = ChatPromptTemplate.from_template("""
You are a market sentiment analyst reading news coverage and filings to gauge investor perception.

Analyze sentiment around this company based ONLY on the context below.

CONTEXT FROM NEWS AND FILINGS:
{context}

Provide a structured sentiment analysis:
1. Media Coverage Tone: Positive, neutral, or negative? Give 2-3 specific examples.
2. Management Tone: Confident, cautious, or defensive?
3. Analyst / Investor Signals: Ratings, upgrades, downgrades, investor activity.
4. Key Themes: Topics dominating the narrative.
5. Overall Sentiment: Positive / Neutral / Negative — brief reason.

Only use information from the context. Be specific.
""")


def run_sentiment_agent(context: str) -> str:
    print("  [AGENT] Running Sentiment Agent...")
    result = invoke_with_fallback(SENTIMENT_PROMPT, {"context": context}, max_tokens=800)
    print("  [AGENT] Sentiment Agent done.")
    return result
