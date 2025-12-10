
# SQL + RAG (Ollama + Chroma + FastAPI) — Demo README

Short: this repo demonstrates a local Retrieval-Augmented-Generation (RAG) pipeline using:
- Ollama (local Llama 3:8B) for embeddings & generation
- Chroma server (v1.x) for vector storage and retrieval
- SQLite for structured data (shop.db)
- FastAPI for a REST demo endpoint

Folders & key files
- `rag/ingest.py` — reads `docs/*.md`, splits, computes embeddings, upserts into Chroma.
- `rag/query.py` — interactive CLI RAG client (embed→retrieve→LLM).
- `api/main.py` — FastAPI app exposing `/ingest`, `/rag`, `/sql`, `/health`.
- `api/db.py` — tiny sqlite helper.
- `docs/` — markdown docs that are indexed by ingestion.
- `data/schema.sql`, `data/seed.sql` — schema and seed for `shop.db`.
- `.env` — runtime config (CHROMA_HOST, CHROMA_PORT, CHROMA_TENANT, CHROMA_DATABASE, OLLAMA_MODEL, SQLITE_PATH).

Prerequisites (local dev)
1. Ollama installed and running locally (model `llama3:8b`).
   ```bash
   ollama serve
3. Chroma CLI installed and run as server:
   ```bash
   chroma run --path chroma_db
