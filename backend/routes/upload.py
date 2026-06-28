import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.config import config
from backend.services.pdf_loader import PDFLoader
from backend.services.embeddings import EmbeddingService
from backend.services.vector_store import VectorStore
from backend.services.mongo_service import MongoService

router = APIRouter()

pdf_loader = PDFLoader()
embedding_service = EmbeddingService(config.EMBEDDING_MODEL)
vector_store = VectorStore()
mongo_service = MongoService()


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...)
):
    """
    Upload and embed a medical PDF.
    Steps:
    1. Save file temporarily
    2. Extract text from PDF
    3. Validate it's a medical document
    4. Chunk + embed with PubMedBERT
    5. Upsert vectors to Pinecone (namespace = session_id)
    6. Save file metadata to MongoDB
    """
    file_path = None
    try:
        # Check file size
        file_content = await file.read()
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > config.MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum allowed size is {config.MAX_FILE_SIZE_MB}MB."
            )

        # Save file temporarily
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(config.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Step 1: Load pages from PDF
        pages = pdf_loader.load_pdf(file_path)
        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. Make sure it's not a scanned image-only PDF.")

        # Step 2: Validate medical document
        is_medical, method = pdf_loader.is_medical_document(pages)
        if not is_medical:
            raise HTTPException(status_code=400, detail="This does not appear to be a medical document. Only lab reports, prescriptions, clinical notes, and similar medical documents are accepted.")

        # Step 3: Chunk + embed
        text = " ".join([p["text"] for p in pages])
        chunks = pdf_loader.chunk_text(text)

        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            embedding = embedding_service.embed_text(chunk)
            embedded_chunks.append({
                "id": f"{session_id}_{file.filename}_{i}",
                "text": chunk,
                "embedding": embedding,
                "file_name": file.filename,
                "chunk_index": i
            })

        # Step 4: Upsert to Pinecone
        chunk_count, vector_ids = vector_store.upsert_chunks(
            chunks=embedded_chunks,
            user_id=session_id
        )

        # Step 5: Save indexed file info to MongoDB
        mongo_service.save_indexed_file(
            user_id=user_id,
            session_id=session_id,
            file_name=file.filename,
            file_path=file_path,
            vector_ids=vector_ids,
            chunk_count=chunk_count
        )

        return {
            "message": "PDF embedded successfully.",
            "file_name": file.filename,
            "chunks_embedded": chunk_count,
            "pages": len(pages),
            "validated_via": method
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
