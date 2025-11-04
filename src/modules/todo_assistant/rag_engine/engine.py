"""
RAG Engine Implementation
=========================

Retrieval-Augmented Generation engine using LangChain for PDF processing.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG Engine for document processing and retrieval.
    
    Uses LangChain with FAISS/Chroma vector stores for efficient similarity search.
    """
    
    def __init__(
        self,
        vector_store: str = "faiss",
        embedding_model: Optional[str] = None,
        persist_directory: Optional[str] = None
    ):
        """
        Initialize RAG Engine.
        
        Args:
            vector_store: Type of vector store ('faiss' or 'chroma')
            embedding_model: Embedding model to use (default: uses project default)
            persist_directory: Directory to persist vector store
        """
        self.vector_store_type = vector_store
        self.embedding_model_name = embedding_model
        self.persist_directory = persist_directory or "./outputs/rag_store"
        self.vector_store = None
        self.documents = []
        
        logger.info(
            "RAG Engine initialized with vector_store=%s, persist_dir=%s",
            vector_store,
            self.persist_directory
        )
        
        # Initialize vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector store backend."""
        try:
            if self.vector_store_type == "faiss":
                self._init_faiss()
            elif self.vector_store_type == "chroma":
                self._init_chroma()
            else:
                raise ValueError(f"Unsupported vector store: {self.vector_store_type}")
        except Exception as e:
            logger.error("Failed to initialize vector store: %s", str(e))
            raise
    
    def _init_faiss(self):
        """Initialize FAISS vector store."""
        try:
            from langchain_community.vectorstores import FAISS
            try:
                from langchain_ollama import OllamaEmbeddings
            except ImportError:
                from langchain_community.embeddings import OllamaEmbeddings
            
            # Use embeddings from project's existing configuration
            embeddings = OllamaEmbeddings(model="mxbai-embed-large")
            
            persist_path = Path(self.persist_directory) / "faiss_index"
            
            # Try to load existing index
            if persist_path.exists():
                logger.info("Loading existing FAISS index from %s", persist_path)
                self.vector_store = FAISS.load_local(
                    str(persist_path),
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                logger.info("Creating new FAISS index")
                # Will be created when documents are added
                self.vector_store = None
                
        except ImportError as e:
            logger.error("FAISS dependencies not available: %s", str(e))
            raise ImportError("Install langchain-community and faiss-cpu to use FAISS")
    
    def _init_chroma(self):
        """Initialize Chroma vector store."""
        try:
            from langchain_community.vectorstores import Chroma
            try:
                from langchain_ollama import OllamaEmbeddings
            except ImportError:
                from langchain_community.embeddings import OllamaEmbeddings
            
            embeddings = OllamaEmbeddings(model="mxbai-embed-large")
            persist_path = Path(self.persist_directory) / "chroma_db"
            
            self.vector_store = Chroma(
                persist_directory=str(persist_path),
                embedding_function=embeddings
            )
            logger.info("Chroma vector store initialized at %s", persist_path)
            
        except ImportError as e:
            logger.error("Chroma dependencies not available: %s", str(e))
            raise ImportError("Install langchain-community and chromadb to use Chroma")
    
    def ingest_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Ingest a PDF document into the RAG system.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with ingestion status and document info
        """
        try:
            from .pdf_processor import PDFProcessor
            
            logger.info("Ingesting PDF: %s", pdf_path)
            
            # Process PDF
            processor = PDFProcessor()
            documents = processor.load_pdf(pdf_path)
            
            if not documents:
                return {
                    "success": False,
                    "error": "No content extracted from PDF",
                    "file": pdf_path
                }
            
            # Add to vector store
            if self.vector_store is None:
                # Create new vector store with first documents
                from langchain_community.vectorstores import FAISS
                try:
                    from langchain_ollama import OllamaEmbeddings
                except ImportError:
                    from langchain_community.embeddings import OllamaEmbeddings
                
                embeddings = OllamaEmbeddings(model="mxbai-embed-large")
                self.vector_store = FAISS.from_documents(documents, embeddings)
            else:
                # Add to existing store
                self.vector_store.add_documents(documents)
            
            self.documents.extend(documents)
            
            # Persist
            self._persist()
            
            return {
                "success": True,
                "file": pdf_path,
                "num_documents": len(documents),
                "total_documents": len(self.documents)
            }
            
        except Exception as e:
            logger.error("Failed to ingest PDF: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "file": pdf_path
            }
    
    def query(
        self,
        query: str,
        k: int = 4,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query: Query string
            k: Number of results to return
            score_threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            Dict with query results
        """
        try:
            if self.vector_store is None:
                return {
                    "success": False,
                    "error": "No documents in RAG system",
                    "query": query
                }
            
            logger.info("Querying RAG system: %s", query)
            
            # Perform similarity search
            if score_threshold:
                results = self.vector_store.similarity_search_with_score(
                    query,
                    k=k
                )
                # Filter by score
                results = [(doc, score) for doc, score in results if score >= score_threshold]
            else:
                docs = self.vector_store.similarity_search(query, k=k)
                results = [(doc, None) for doc in docs]
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
            
            return {
                "success": True,
                "query": query,
                "num_results": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            logger.error("Query failed: %s", str(e))
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _persist(self):
        """Persist the vector store to disk."""
        try:
            if self.vector_store is None:
                return
            
            persist_path = Path(self.persist_directory)
            persist_path.mkdir(parents=True, exist_ok=True)
            
            if self.vector_store_type == "faiss":
                save_path = persist_path / "faiss_index"
                self.vector_store.save_local(str(save_path))
                logger.info("FAISS index saved to %s", save_path)
            elif self.vector_store_type == "chroma":
                # Chroma persists automatically
                logger.info("Chroma vector store persisted")
                
        except Exception as e:
            logger.error("Failed to persist vector store: %s", str(e))
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dict with system statistics
        """
        return {
            "vector_store_type": self.vector_store_type,
            "num_documents": len(self.documents),
            "persist_directory": self.persist_directory,
            "initialized": self.vector_store is not None
        }
