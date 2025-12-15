
# SQL + RAG (Ollama + Chroma + FastAPI + PySpark)

A complete backend project demonstrating SQL CRUD operations, Retrieval-Augmented Generation (RAG), PySpark analytics, and integration with a self-hosted Ollama LLM model.  
The system is designed to showcase backend engineering, AI architecture, data engineering using PySpark, and DevOps skills (Docker and Kubernetes ready).

---

## Features

### Backend (FastAPI)
- SQLite database (`shop.db`)
- FAST API endpoints for:
  - customers
  - products
  - orders
  - order_items
- Environment-based configuration

### Retrieval-Augmented Generation (RAG)
- Chroma vector database
- Embeddings and inference using Ollama (llama3:8b)
- Optional cloud LLM providers (OpenAI, Groq, Anthropic)

### Analytics (PySpark)
- CSV export from SQLite tables
- Spark SQL analytics:
  - Top products by revenue
  - Top customers by spending

### DevOps (TODO)
- Dockerfile included
- Kubernetes manifests (Deployment, Service, Secrets)
- Self-hosted Ollama kept outside cluster for simplicity

---

# Architecture


Folders & key files
- `rag/ingest.py` — reads `docs/*.md`, splits, computes embeddings, upserts into Chroma.
- `rag/query.py` — interactive CLI RAG client (embed→retrieve→LLM).
- `api/main.py` — FastAPI app exposing `/ingest`, `/rag`, `/sql`, `/health`.
- `api/db.py` — tiny sqlite helper.
- `docs/` — markdown docs that are indexed by ingestion.
- `data/schema.sql`, `data/seed.sql` — schema and seed for `shop.db`.
- `.env` — runtime config (CHROMA_HOST, CHROMA_PORT, CHROMA_TENANT, CHROMA_DATABASE, OLLAMA_MODEL, SQLITE_PATH).

Prerequisites (local dev)
1. Ollama installed and `ollama serve` running locally (model `llama3:8b` pulled).
2. Chroma CLI installed and run as server:
   ```bash
   chroma run --path chroma_db









   
