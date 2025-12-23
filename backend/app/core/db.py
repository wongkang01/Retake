import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings as ChromaSettings
from google import genai
from app.core.config import get_settings
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)
settings = get_settings()

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, model_name: str = "models/text-embedding-004"):
        # The new SDK uses a centralized Client object.
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        if not input:
            return []
            
        embeddings = []
        # TODO: Implement batching for production efficiency
        for text in input:
            try:
                # The new SDK method for embeddings
                # Note: 'task_type' logic might differ in the new SDK or be part of config.
                # For basic text-embedding-004, simple content passing usually works.
                # We'll stick to the standard call structure.
                result = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text,
                    config={"task_type": "RETRIEVAL_DOCUMENT"} 
                )
                embeddings.append(result.embeddings[0].values)
            except Exception as e:
                logger.error(f"Error embedding content with Gemini: {e}")
                raise e
        return embeddings

class ChromaService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(allow_reset=True)
        )
        
        if settings.GEMINI_API_KEY:
            # Updating to the newer model which is standard for the new SDK
            self.embedding_fn = GeminiEmbeddingFunction(
                api_key=settings.GEMINI_API_KEY,
                model_name="models/text-embedding-004"
            )
        else:
            logger.warning("GEMINI_API_KEY not set. Using default ChromaDB embedding.")
            self.embedding_fn = None # Uses Chroma default (all-MiniLM-L6-v2)

    def get_collection(self, name: str):
        """
        Get or create a collection with the configured embedding function.
        """
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"} # Optimized for semantic similarity
        )

# Global instance
_chroma_service = None

def get_chroma_service():
    global _chroma_service
    if _chroma_service is None:
        _chroma_service = ChromaService()
    return _chroma_service