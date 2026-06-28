from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.mongo_service import MongoService

router = APIRouter()
mongo_service = MongoService()


class RenameRequest(BaseModel):
    title: str


# ══════════════════════════════════════════════════════
# CHAT HISTORY
# ══════════════════════════════════════════════════════

@router.get("/history/{user_id}/{session_id}")
async def get_history(user_id: str, session_id: str):
    messages = mongo_service.get_history(user_id, session_id)
    return {"messages": messages}


@router.delete("/history/{user_id}/{session_id}")
async def clear_history(user_id: str, session_id: str):
    mongo_service.clear_history(user_id, session_id)
    return {"status": "cleared"}


# ══════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ══════════════════════════════════════════════════════

@router.get("/sessions/{user_id}")
async def get_sessions(user_id: str):
    sessions = mongo_service.get_user_sessions(user_id)
    return {"sessions": sessions}




@router.post("/sessions/{user_id}/{session_id}")
async def create_session(user_id: str, session_id: str, title: str = "New Record"):
    mongo_service.create_session(user_id, session_id, title)
    return {"status": "created"}


@router.put("/sessions/{session_id}/rename")
async def rename_session(session_id: str, body: RenameRequest):
    mongo_service.update_session_title(session_id, body.title)
    return {"status": "renamed"}


@router.put("/sessions/{session_id}/pin")
async def pin_session(session_id: str):
    new_state = mongo_service.toggle_pin(session_id)
    return {"pinned": new_state}



@router.delete("/sessions/{user_id}/{session_id}/permanent")
async def permanent_delete_session(user_id: str, session_id: str):
    """Permanently delete a session and all its data."""
    try:
        mongo_service.permanent_delete_session(user_id, session_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════
# SESSION FILES
# ══════════════════════════════════════════════════════

@router.get("/session-files/{session_id}")
async def get_session_files(session_id: str):
    """Get all indexed and recycled files for a session."""
    indexed = mongo_service.get_indexed_files(session_id)
    recycled = mongo_service.get_recycled_files(session_id)
    return {
        "indexed_files": indexed,
        "recycled_files": recycled
    }
