"""
embedder.py
-----------
Converts text chunks into embeddings and stores them in a FAISS vector database.

What are embeddings?
  An embedding is a list of numbers that represents the "meaning" of a piece of text.
  Two sentences with similar meaning will have similar numbers (close in vector space).
  This is how the retriever later finds relevant chunks — by comparing number lists,
  not by keyword matching.

What is FAISS?
  FAISS (Facebook AI Similarity Search) is a library that stores embeddings and
  lets you search them very fast. Think of it as a search engine for meaning.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns a free local HuggingFace embeddings model.
    Downloads once (~90MB), then runs entirely on your machine — no API calls, no cost.
    Model: all-MiniLM-L6-v2 — fast, small, and great for semantic search.
    """
    print("  [EMBEDDER] Loading HuggingFace embeddings model (downloads once ~90MB)...")
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


def build_vectorstore(chunks: list[str], save_path: str = "data/vectorstore") -> FAISS:
    """
    Takes a list of text chunks, converts them to embeddings, and saves
    the result as a FAISS index to disk.

    Args:
        chunks:     List of text strings from chunker.py
        save_path:  Folder to save the FAISS index. Default: 'data/vectorstore'

    Returns:
        A FAISS vectorstore object (can be queried immediately).
    """
    print(f"  [EMBEDDER] Creating embeddings for {len(chunks)} chunks (runs locally)...")

    embeddings = get_embeddings()
    vectorstore = FAISS.from_texts(chunks, embeddings)

    os.makedirs(save_path, exist_ok=True)
    vectorstore.save_local(save_path)

    print(f"  [EMBEDDER] Saved FAISS index to: {save_path}")
    return vectorstore


def load_vectorstore(save_path: str = "data/vectorstore") -> FAISS:
    """
    Loads a previously saved FAISS index from disk.
    Use this to avoid re-embedding the same document every run.

    Args:
        save_path: Folder where the FAISS index was saved.

    Returns:
        A FAISS vectorstore object ready to query.
    """
    print(f"  [EMBEDDER] Loading FAISS index from: {save_path}")
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        save_path,
        embeddings,
        allow_dangerous_deserialization=True  # Required by newer LangChain versions
    )
    print(f"  [EMBEDDER] Index loaded successfully.")
    return vectorstore
