"""
chunker.py
----------
Splits a large document (like a 10-K filing) into smaller, overlapping chunks.

Why do we chunk?
  LLMs can only read a limited amount of text at once (called a "context window").
  A 10-K filing can be 1M+ characters — way too big to feed in all at once.
  We split it into small pieces (~1000 characters each) so the RAG retriever
  can find and return only the most relevant pieces for each query.

Why overlap?
  Each chunk overlaps slightly with the next (200 chars by default) so that
  important sentences don't get cut off at chunk boundaries.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Splits a long text string into a list of smaller chunks.

    Args:
        text:          The full document text (e.g. a 10-K filing).
        chunk_size:    Max characters per chunk. Default: 1000.
        chunk_overlap: Characters of overlap between adjacent chunks. Default: 200.

    Returns:
        A list of text strings (chunks).

    Example:
        chunks = chunk_documents(filing_text)
        print(f"Split into {len(chunks)} chunks")
        print(chunks[0])  # First chunk
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Try splitting at these boundaries in order: paragraphs → lines → sentences → words
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(text)
    print(f"  [CHUNKER] Split into {len(chunks)} chunks "
          f"(size={chunk_size}, overlap={chunk_overlap})")
    return chunks
