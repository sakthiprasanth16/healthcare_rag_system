from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.config import config
from backend.services.embeddings import EmbeddingService
from backend.services.vector_store import VectorStore
from backend.services.llm_service import LLMService
from backend.services.mongo_service import MongoService

router = APIRouter()

embedding_service = EmbeddingService(config.EMBEDDING_MODEL)
vector_store = VectorStore()
llm_service = LLMService()
mongo_service = MongoService()


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    question: str


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    RAG Chat endpoint.
    1. Embed the user question
    2. Search Pinecone (namespace = session_id)
    3. Filter out recycled (soft-deleted) documents
    4. Get chat history from MongoDB
    5. Generate answer with Gemini
    6. Save messages to MongoDB
    """
    try:
        # 1. Embed question
        query_embedding = embedding_service.embed_text(request.question)

        # 2. Search Pinecone using session_id as namespace
        chunks = vector_store.search(
            query_embedding=query_embedding,
            user_id=request.session_id,
            top_k=config.TOP_K
        )

        # 3. Filter out recycled (soft-deleted) documents
        recycled_files = mongo_service.get_recycled_files(request.session_id)
        if recycled_files:
            chunks = [c for c in chunks if c["file_name"] not in recycled_files]

        # 4. Get chat history from MongoDB
        history = mongo_service.get_history(request.user_id, request.session_id)

        # 5. Generate answer
        result = llm_service.generate_answer(
            question=request.question,
            context_chunks=chunks,
            chat_history=history
        )

        # 6. Save to MongoDB
        mongo_service.save_message(
            user_id=request.user_id,
            session_id=request.session_id,
            role="user",
            content=request.question
        )
        mongo_service.save_message(
            user_id=request.user_id,
            session_id=request.session_id,
            role="assistant",
            content=result["answer"],
            sources=result["sources"]
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
