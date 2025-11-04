"""
PDF Processing for RAG
=======================

Extract and process text from PDF documents for RAG ingestion.
"""

import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF documents for RAG ingestion."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info("PDF Processor initialized with chunk_size=%d", chunk_size)
    
    def load_pdf(self, pdf_path: str) -> List:
        """
        Load and process a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of LangChain Document objects
        """
        try:
            from langchain_community.document_loaders import PyPDFLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
            logger.info("Loading PDF: %s", pdf_path)
            
            # Verify file exists
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            logger.info("Loaded %d pages from PDF", len(documents))
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len
            )
            
            chunks = text_splitter.split_documents(documents)
            logger.info("Split into %d chunks", len(chunks))
            
            # Add source metadata
            for chunk in chunks:
                chunk.metadata["source"] = pdf_path
                chunk.metadata["type"] = "pdf"
            
            return chunks
            
        except ImportError as e:
            logger.error("PDF processing dependencies not available: %s", str(e))
            raise ImportError("Install pypdf and langchain-community to process PDFs")
        except Exception as e:
            logger.error("Failed to load PDF: %s", str(e))
            raise
