"""
retriever.py
------------
Queries the FAISS vector database and returns the most relevant text chunks
for a given question or topic.

How it works:
  You ask a question like "What is the company's revenue trend?"
  The retriever converts that question to an embedding, then finds the
  chunks in FAISS whose embeddings are closest (most similar in meaning).
  It returns the top-k matching chunks as a single string — ready to be
  passed into an LLM agent as context.
"""

from langchain_community.vectorstores import FAISS


def retrieve_context(vectorstore: FAISS, query: str, k: int = 6) -> str:
    """
    Retrieves the top-k most relevant chunks from the vectorstore for a query.

    Args:
        vectorstore: A FAISS vectorstore (from embedder.py)
        query:       The search query, e.g. "revenue and profit growth"
        k:           Number of chunks to retrieve. Default: 6.
                     Higher k = more context for the agent, but more tokens used.

    Returns:
        A single string of all retrieved chunks joined together.
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)

    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    print(f"  [RETRIEVER] Retrieved {len(docs)} chunks for query: '{query[:60]}...'")
    return context


def retrieve_multi(vectorstore: FAISS, queries: list[str], k: int = 4) -> str:
    """
    Retrieves context for multiple queries and combines the results.
    Useful when an agent needs information on several different topics.

    Args:
        vectorstore: A FAISS vectorstore
        queries:     List of search queries
        k:           Chunks per query

    Returns:
        Combined context string from all queries (deduplicated).
    """
    seen = set()
    all_chunks = []

    for query in queries:
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(query)
        for doc in docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                all_chunks.append(doc.page_content)

    context = "\n\n---\n\n".join(all_chunks)
    print(f"  [RETRIEVER] Retrieved {len(all_chunks)} unique chunks across {len(queries)} queries.")
    return context
