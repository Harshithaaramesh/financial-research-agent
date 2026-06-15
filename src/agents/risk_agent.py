from langchain_core.prompts import ChatPromptTemplate
from src.utils.llm import invoke_with_fallback

RISK_PROMPT = ChatPromptTemplate.from_template("""
You are a risk analyst at a major financial institution identifying corporate risks for investment decisions.

Identify all risks and concerns from the context below. Be thorough but concise.

CONTEXT FROM SEC FILING AND NEWS:
{context}

Provide a structured risk assessment:
1. Legal & Regulatory Risks: Lawsuits, investigations, compliance issues.
2. Market Risks: Interest rate, credit, liquidity, volatility.
3. Operational Risks: Business disruptions, technology, key-person dependency.
4. Macroeconomic Risks: Economic slowdown, geopolitical, inflation.
5. Management Warnings: Risks flagged by management in the filing.
6. Overall Risk Level: Low / Medium / High — and why.

Only use information from the context. Say "none identified" if a category isn't mentioned.
""")


def run_risk_agent(context: str) -> str:
    print("  [AGENT] Running Risk Agent...")
    result = invoke_with_fallback(RISK_PROMPT, {"context": context}, max_tokens=800)
    print("  [AGENT] Risk Agent done.")
    return result
