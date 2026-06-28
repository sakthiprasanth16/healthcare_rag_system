from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import upload, chat, history, document

app = FastAPI(
    title="Healthcare RAG API",
    description="Patient Medical Record Assistant — Powered by PubMedBERT + Gemini",
    version="1.0.0"
)

# CORS — allow Streamlit frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, tags=["Upload"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(history.router, tags=["Sessions & History"])
app.include_router(document.router, tags=["Document Management"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Healthcare RAG API is running."}
