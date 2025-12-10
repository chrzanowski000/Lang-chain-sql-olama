conda create -n sqlrag python=3.10 -y
conda activate sqlrag
pip install -r requirements.txt


sqlite3 shop.db < data/schema.sql
sqlite3 shop.db < data/seed.sql

chroma run --path chroma_db
ollama serve


conda activate sqlrag
python rag/ingest.py
python rag/query.py

uvicorn api.main:app --reload --host 0.0.0.0 --port 8080

curl -s http://localhost:8080/health | jq .
curl -s -X POST http://localhost:8080/ingest | jq .


curl -s -X POST http://localhost:8080/ingest | jq .
curl -s -X POST http://localhost:8080/rag -H "Content-Type: application/json" \
  -d '{"query":"What does the order_items table store?","k":4}' | jq .
curl -s -X POST http://localhost:8080/sql -H "Content-Type: application/json" \
  -d '{"sql":"SELECT o.id, c.name, SUM(oi.quantity*oi.unit_price) AS total FROM orders o JOIN customers c ON c.id=o.customer_id JOIN order_items oi ON oi.order_id=o.id GROUP BY o.id;"}' | jq .
