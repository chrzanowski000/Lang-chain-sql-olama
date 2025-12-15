
# SQL + RAG (Ollama + Chroma + FastAPI + PySpark)

A complete backend project demonstrating Retrieval-Augmented Generation (RAG), SQL operations, PySpark analytics, and integration with a self-hosted Ollama LLM model.  System has integrated FastAPI that can perform hybrid RAG and SQL tasks as well as PySpark predefined analytics.

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

## Installation
```
git clone <your-repo>
cd Lang-chain-sql-ollama

```
```
conda create -n sqlrag python=3.10 -y
conda activate sqlrag
pip install -r requirements.txt
```
### Create `.env`
```
SQLITE_PATH=./shop.db

CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_TENANT=default_tenant
CHROMA_DATABASE=default_db

OLLAMA_MODEL=llama3:8b
```
### Database Setup
```
sqlite3 shop.db < data/schema.sql
sqlite3 shop.db < data/seed.sql
```
### RAG Ingestion
Start Chroma database
```
chroma run --path chroma_db
```
Run ingestion
```
python rag/ingest.py
```
### Start API
```
uvicorn api.main:app --reload --port 8080
```

## API Examples

## PySpark


Folders & key files
- `rag/ingest.py` — reads `docs/*.md`, splits, computes embeddings, upserts into Chroma.
- `rag/query.py` — interactive CLI RAG client (embed→retrieve→LLM).
- `api/main.py` — FastAPI app exposing `/ingest`, `/rag`, `/sql`, `/health`.
- `api/db.py` — sqlite helper.
- `docs/` — markdown docs that are indexed by ingestion.
- `data/schema.sql`, `data/seed.sql` — schema and seed for `shop.db`.
- `.env` — runtime config (CHROMA_HOST, CHROMA_PORT, CHROMA_TENANT, CHROMA_DATABASE, OLLAMA_MODEL, SQLITE_PATH).











   
