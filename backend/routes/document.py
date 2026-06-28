from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.mongo_service import MongoService
from backend.services.vector_store import VectorStore

router = APIRouter()
mongo_service = MongoService()
vector_store = VectorStore()


class DocumentRequest(BaseModel):
    user_id: str
    session_id: str
    file_name: str


# ────────────────────────────────────────────
# RECYCLE — Soft delete (hide from chat)
# ────────────────────────────────────────────
@router.post("/document/recycle")
async def recycle_document(req: DocumentRequest):
    """Move a document to the recycle bin (soft delete). Vectors remain in Pinecone."""
    try:
        mongo_service.move_to_recycle(req.user_id, req.session_id, req.file_name)
        return {"message": f"{req.file_name} moved to recycle bin."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ────────────────────────────────────────────
# RESTORE — Bring back from recycle bin
# ────────────────────────────────────────────
@router.post("/document/restore")
async def restore_document(req: DocumentRequest):
    """Restore a document from the recycle bin back to active use."""
    try:
        mongo_service.restore_from_recycle(req.session_id, req.file_name)
        return {"message": f"{req.file_name} restored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ────────────────────────────────────────────
# PERMANENT DELETE — Wipe from Pinecone + MongoDB
# ────────────────────────────────────────────
@router.delete("/document/permanent")
async def permanent_delete(req: DocumentRequest):
    """Permanently delete a document — removes vectors from Pinecone and records from MongoDB."""
    try:
        # Get vector IDs from MongoDB (checks both indexed_files and recycle_bin)
        vector_ids = mongo_service.get_vector_ids(req.session_id, req.file_name)

        if vector_ids:
            # Delete vectors from Pinecone
            vector_store.delete_vectors(vector_ids=vector_ids, namespace=req.session_id)

        # Remove records from MongoDB
        mongo_service.permanent_delete_file(req.session_id, req.file_name)

        return {"message": f"{req.file_name} permanently deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
