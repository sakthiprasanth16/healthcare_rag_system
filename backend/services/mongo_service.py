from pymongo import MongoClient, DESCENDING
from datetime import datetime, timezone
from backend.config import config


class MongoService:
    def __init__(self):
        self.client = MongoClient(config.MONGO_URI)
        self.db = self.client[config.MONGO_DB_NAME]

        # Collections
        self.messages = self.db["messages"]
        self.sessions = self.db["sessions"]
        self.indexed_files = self.db["indexed_files"]
        self.recycle_bin = self.db["document_recycle_bin"]

        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes for performance."""
        self.messages.create_index([("user_id", 1), ("session_id", 1)])
        self.sessions.create_index([("user_id", 1)])
        self.sessions.create_index([("session_id", 1)], unique=True)
        self.indexed_files.create_index([("session_id", 1)])

    # ══════════════════════════════════════════════════════
    # SESSION MANAGEMENT
    # ══════════════════════════════════════════════════════

    def create_session(self, user_id: str, session_id: str, title: str = "New Record"):
        now = datetime.now(timezone.utc).isoformat()
        self.sessions.update_one(
            {"session_id": session_id},
            {"$setOnInsert": {
                "user_id": user_id,
                "session_id": session_id,
                "title": title,
                "pinned": False,
                "created_at": now,
                "updated_at": now
            }},
            upsert=True
        )

    def get_user_sessions(self, user_id: str) -> list:
        sessions = list(self.sessions.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("updated_at", DESCENDING))
        return sessions


    def update_session_title(self, session_id: str, title: str):
        now = datetime.now(timezone.utc).isoformat()
        self.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"title": title, "updated_at": now}}
        )

    def touch_session(self, session_id: str):
        """Update session's updated_at timestamp."""
        now = datetime.now(timezone.utc).isoformat()
        self.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"updated_at": now}}
        )

    def toggle_pin(self, session_id: str) -> bool:
        session = self.sessions.find_one({"session_id": session_id})
        if not session:
            return False
        new_state = not session.get("pinned", False)
        self.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"pinned": new_state}}
        )
        return new_state


    def permanent_delete_session(self, user_id: str, session_id: str):
        """Permanently delete session, its messages, and indexed file records."""
        self.sessions.delete_one({"session_id": session_id})
        self.messages.delete_many({"session_id": session_id})
        self.indexed_files.delete_many({"session_id": session_id})
        self.recycle_bin.delete_many({"session_id": session_id})

    # ══════════════════════════════════════════════════════
    # CHAT HISTORY
    # ══════════════════════════════════════════════════════

    def save_message(self, user_id: str, session_id: str, role: str, content: str, sources: list = None):
        now = datetime.now(timezone.utc).isoformat()
        self.messages.insert_one({
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "created_at": now
        })
        self.touch_session(session_id)

    def get_history(self, user_id: str, session_id: str, limit: int = 20) -> list:
        msgs = list(self.messages.find(
            {"user_id": user_id, "session_id": session_id},
            {"_id": 0}
        ).sort("created_at", 1).limit(limit))
        return msgs

    def clear_history(self, user_id: str, session_id: str):
        self.messages.delete_many({"user_id": user_id, "session_id": session_id})

    # ══════════════════════════════════════════════════════
    # DOCUMENT / FILE MANAGEMENT
    # ══════════════════════════════════════════════════════

    def save_indexed_file(self, user_id: str, session_id: str, file_name: str,
                          file_path: str, vector_ids: list, chunk_count: int):
        now = datetime.now(timezone.utc).isoformat()
        self.indexed_files.update_one(
            {"session_id": session_id, "file_name": file_name},
            {"$set": {
                "user_id": user_id,
                "session_id": session_id,
                "file_name": file_name,
                "file_path": file_path,
                "vector_ids": vector_ids,
                "chunk_count": chunk_count,
                "indexed_at": now
            }},
            upsert=True
        )

    def get_indexed_files(self, session_id: str) -> list:
        files = list(self.indexed_files.find(
            {"session_id": session_id},
            {"_id": 0}
        ))
        return files

    def get_recycled_files(self, session_id: str) -> list:
        """Returns list of recycled file names for a session."""
        docs = list(self.recycle_bin.find(
            {"session_id": session_id},
            {"_id": 0, "file_name": 1}
        ))
        return [d["file_name"] for d in docs]

    def get_vector_ids(self, session_id: str, file_name: str) -> list:
        doc = self.indexed_files.find_one(
            {"session_id": session_id, "file_name": file_name}
        )
        if doc:
            return doc.get("vector_ids", [])
        # Also check recycle bin
        doc = self.recycle_bin.find_one(
            {"session_id": session_id, "file_name": file_name}
        )
        return doc.get("vector_ids", []) if doc else []

    def move_to_recycle(self, user_id: str, session_id: str, file_name: str):
        """Soft delete — move file record to recycle bin."""
        doc = self.indexed_files.find_one(
            {"session_id": session_id, "file_name": file_name},
            {"_id": 0}
        )
        if not doc:
            return
        now = datetime.now(timezone.utc).isoformat()
        self.recycle_bin.update_one(
            {"session_id": session_id, "file_name": file_name},
            {"$set": {**doc, "recycled_at": now}},
            upsert=True
        )
        self.indexed_files.delete_one({"session_id": session_id, "file_name": file_name})

    def restore_from_recycle(self, session_id: str, file_name: str):
        """Restore file from recycle bin back to indexed_files."""
        doc = self.recycle_bin.find_one(
            {"session_id": session_id, "file_name": file_name},
            {"_id": 0}
        )
        if not doc:
            return
        doc.pop("recycled_at", None)
        self.indexed_files.update_one(
            {"session_id": session_id, "file_name": file_name},
            {"$set": doc},
            upsert=True
        )
        self.recycle_bin.delete_one({"session_id": session_id, "file_name": file_name})

    def permanent_delete_file(self, session_id: str, file_name: str):
        """Remove file record from both indexed_files and recycle_bin."""
        self.indexed_files.delete_one({"session_id": session_id, "file_name": file_name})
        self.recycle_bin.delete_one({"session_id": session_id, "file_name": file_name})
