import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    # Pinecone Settings
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "healthcare-rag")

    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "healthcare_rag")

    # Embedding Model
    EMBEDDING_MODEL = "NeuML/pubmedbert-base-embeddings"
    EMBEDDING_DIMENSION = 768

    # LLM — configurable via .env, defaults to stable model
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")

    # Chunking — optimized for medical PDFs
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150

    # Retrieval
    TOP_K = 5

    # Paths
    UPLOAD_DIR = "data/uploaded_pdfs"

    # Upload limit (20MB)
    MAX_FILE_SIZE_MB = 20

config = Config()
