
# AGENT: SQL + RAG (Ollama + Chroma + FastAPI + PySpark)

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
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

## API endpoints examples
Get Health
```
curl -s http://localhost:8080/health | jq .
```
Perform ingestion
```
curl -s -X POST http://localhost:8080/ingest | jq .
```
RAG query
```
curl -s -X POST http://localhost:8080/rag \
-H "Content-Type: application/json" \
-d '{"query":"What does the order_items table store?","k":4}' | jq .
```
SQL query
```
curl -s -X POST http://localhost:8080/sql -H "Content-Type: application/json" \
  -d '{"sql":"SELECT o.id, c.name, SUM(oi.quantity*oi.unit_price) AS total FROM orders o JOIN customers c ON c.id=o.customer_id JOIN order_items oi ON oi.order_id=o.id GROUP BY o.id;"}' | jq .
```
SQL question - LLM creates SQL query on its own
```
curl -s -X POST http://localhost:8080/rag -H "Content-Type: application/json" \
  -d '{"query":"What is the most expensive product in the shop?","k":4}' | jq .
```
Adding data
```
curl -s -X POST http://localhost:8080/create_customer \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "country": "USA"}'
```
```
curl -s -X POST http://localhost:8080/create_product \
  -H "Content-Type: application/json" \
  -d '{"name":"Gaming Mouse","category":"Electronics","price":60}'
```
```
curl -s -X POST http://localhost:8080/create_order \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"order_date":"2024-01-01"}'
```
```
curl -s -X POST http://localhost:8080/create_order_item \
  -H "Content-Type: application/json" \
  -d '{"order_id":1,"product_id":3,"quantity":2,"unit_price":60}'
```
## PySpark
Return top products by total revenue computed in Spark
```
curl "http://localhost:8080/spark/top_products?limit=5" | jq .
```
Return top customers by total spend computed with Spark
```
curl "http://localhost:8080/spark/customers_spend?limit=5" | jq .
```

Folders & key files
- `rag/ingest.py` — reads `docs/*.md`, splits, computes embeddings, upserts into Chroma.
- `rag/query.py` — interactive CLI RAG client (embed→retrieve→LLM).
- `api/main.py` — FastAPI app exposing `/ingest`, `/rag`, `/sql`, `/health`.
- `api/db.py` — sqlite helper.
- `docs/` — markdown docs that are indexed by ingestion.
- `data/schema.sql`, `data/seed.sql` — schema and seed for `shop.db`.
- `.env` — runtime config (CHROMA_HOST, CHROMA_PORT, CHROMA_TENANT, CHROMA_DATABASE, OLLAMA_MODEL, SQLITE_PATH).











   
