# ── Healthcare RAG — Backend Dockerfile ─────────────────────────────────────
# FastAPI + PubMedBERT (sentence-transformers) + Pinecone + Gemini + MongoDB
#
# IMPORTANT: main.py does "from backend.routes import ..." so this container
# must run uvicorn from the PROJECT ROOT, not from inside backend/. That's why
# WORKDIR is /app (the root) and we COPY backend/ into /app/backend/ — do not
# flatten this structure or the import will break.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# build-essential: some packages compile native extensions if no wheel matches
# curl: used by the HEALTHCHECK below
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install deps first (cached layer unless requirements.txt changes).
# NOTE: sentence-transformers pulls in torch — this is a HEAVY install
# (several minutes, 1GB+ of packages). That's expected, not an error.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend package. Kept at /app/backend so "backend.main:app"
# resolves correctly as a Python package import.
COPY backend/ ./backend/

# Runtime folder for temporary PDF uploads (gitignored, so it won't exist
# in the build context unless created here)
RUN mkdir -p /app/data/uploaded_pdfs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
