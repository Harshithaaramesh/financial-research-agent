from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import invoke_with_fallback

COORDINATOR_PROMPT = ChatPromptTemplate.from_template("""
You are a Senior Research Analyst at a top-tier investment bank synthesizing specialist reports on {company}.

Write one professional investment memo. Do not introduce information not already in the reports below.

FUNDAMENTALS:
{fundamentals}

RISK:
{risk}

SENTIMENT:
{sentiment}

Use this exact structure:

# Investment Research Memo: {company}

## Executive Summary
(2-3 sentences on the overall picture)

## Financial Highlights
(Key numbers and trends)

## Risk Assessment
(Top risks with severity)

## Market Sentiment
(Public and investor perception)

## Overall Assessment
(Balanced conclusion — strong or concerning position?)

Keep the tone professional, concise, and factual.
""")


def run_coordinator_agent(company: str, fundamentals: str, risk: str, sentiment: str) -> str:
    print("  [AGENT] Running Coordinator Agent...")
    result = invoke_with_fallback(
        COORDINATOR_PROMPT,
        {"company": company, "fundamentals": fundamentals, "risk": risk, "sentiment": sentiment},
        max_tokens=1500,
    )
    print("  [AGENT] Coordinator Agent done.")
    return result
