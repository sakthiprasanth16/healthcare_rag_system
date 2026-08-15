# ── Healthcare RAG — Frontend Dockerfile ────────────────────────────────────
# Streamlit UI. Talks to the backend via the BACKEND_URL env var (see
# streamlit_app.py: requests.post(f"{BACKEND_URL}/chat", ...)) — no nginx
# proxy needed here, unlike the previous project.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Same requirements.txt as backend (single shared file in this repo).
# This does install torch/sentence-transformers/pinecone here too even
# though the frontend doesn't need them — harmless but adds build time.
# See note below if you want to trim this down.
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ ./frontend/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "frontend/streamlit_app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
