"""
graph.py
--------
Orchestrates all agents using LangGraph.

What is LangGraph?
  LangGraph lets you define a "graph" of AI agents where each node is one agent,
  and edges define the order in which they run.

Our graph structure:
    START
      │
      ▼
  [fundamentals] ──┐
  [risk]          ──┼──► [coordinator] ──► END
  [sentiment]    ──┘

The three specialist agents run sequentially (one after another), then
the coordinator collects all three results and writes the final memo.

Note: LangGraph supports true parallel execution too — that's an advanced
extension you can add later once you're comfortable with the basics.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from src.agents.fundamentals_agent import run_fundamentals_agent
from src.agents.risk_agent import run_risk_agent
from src.agents.sentiment_agent import run_sentiment_agent
from src.agents.coordinator_agent import run_coordinator_agent


# State: the shared data that flows between all nodes 
# Think of this as a "baton" passed from agent to agent.
# Each agent reads from it and adds its result back into it.

class ResearchState(TypedDict):
    company: str       # Company name, e.g. "JPMorgan Chase"
    context: str       # Retrieved chunks from RAG (shared by all agents)
    fundamentals: str  # Output of fundamentals_agent
    risk: str          # Output of risk_agent
    sentiment: str     # Output of sentiment_agent
    final_report: str  # Output of coordinator_agent (the final memo)


# Node functions 
# Each node receives the full state, does its job, and returns ONLY the
# keys it changed (LangGraph merges the result back into state automatically).

def fundamentals_node(state: ResearchState) -> dict:
    result = run_fundamentals_agent(state["context"])
    return {"fundamentals": result}


def risk_node(state: ResearchState) -> dict:
    result = run_risk_agent(state["context"])
    return {"risk": result}


def sentiment_node(state: ResearchState) -> dict:
    result = run_sentiment_agent(state["context"])
    return {"sentiment": result}


def coordinator_node(state: ResearchState) -> dict:
    result = run_coordinator_agent(
        company=state["company"],
        fundamentals=state["fundamentals"],
        risk=state["risk"],
        sentiment=state["sentiment"],
    )
    return {"final_report": result}


# Build the graph 

def build_graph():
    """
    Constructs and compiles the LangGraph agent pipeline.

    Returns:
        A compiled LangGraph app ready to run with .invoke()

    Usage:
        graph = build_graph()
        result = graph.invoke({
            "company": "JPMorgan Chase",
            "context": "...retrieved text...",
            "fundamentals": "",
            "risk": "",
            "sentiment": "",
            "final_report": "",
        })
        print(result["final_report"])
    """
    builder = StateGraph(ResearchState)

    # Register each agent as a node
    builder.add_node("fundamentals", fundamentals_node)
    builder.add_node("risk", risk_node)
    builder.add_node("sentiment", sentiment_node)
    builder.add_node("coordinator", coordinator_node)

    # Define execution order
    builder.add_edge(START, "fundamentals")
    builder.add_edge("fundamentals", "risk")
    builder.add_edge("risk", "sentiment")
    builder.add_edge("sentiment", "coordinator")
    builder.add_edge("coordinator", END)

    return builder.compile()
