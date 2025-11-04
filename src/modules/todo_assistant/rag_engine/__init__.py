"""
RAG Engine for PDF Manual Processing
====================================

LangChain-based RAG system for ingesting and querying PDF manuals.
Supports FAISS and Chroma vector stores.
"""

from .engine import RAGEngine
from .pdf_processor import PDFProcessor

__all__ = ["RAGEngine", "PDFProcessor"]
