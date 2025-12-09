
import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from typing import List

load_dotenv() #here .env is loaded
from api import db as dbmod
from api import schemas

# Langchain / Ollama / Chroma imports
from chromadb import HttpClient
from langchain_ollama import ChatOllama, OllamaEmbeddings

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8000))
CHROMA_TENANT = os.environ.get("CHROMA_TENANT", "default_tenant")
CHROMA_DB = os.environ.get("CHROMA_DATABASE", "default_db")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:8b")

app = FastAPI(title="SQL + RAG demo")

# Initialize LLM/emb client
_llm = None
_emb = None
_col = None
_client = None

def get_chroma_client():
    global _client, _col
    if _client is None:
        _client = HttpClient(host=CHROMA_HOST, port=CHROMA_PORT, tenant=CHROMA_TENANT, database=CHROMA_DB)
    return _client

def get_collection():
    global _col
    if _col is None:
        client = get_chroma_client()
        try:
            _col = client.get_collection("docs")
        except Exception:
            _col = client.create_collection("docs", metadata={"hnsw:space":"cosine"})
    return _col

def get_llm_and_emb():
    global _llm, _emb
    if _llm is None:
        _llm = ChatOllama(model=OLLAMA_MODEL, temperature=0.0)
    if _emb is None:
        _emb = OllamaEmbeddings(model=OLLAMA_MODEL)
    return _llm, _emb

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/sql", response_model=schemas.SQLResponse)
def run_sql(req: schemas.SQLRequest):
    try:
        if req.sql.strip().lower().startswith("select"):
            rows = dbmod.run_select(req.sql)
            return {"result": rows}
        else:
            res = dbmod.run_exec(req.sql)
            return {"result": [], "rows_affected": res["rows_affected"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# @app.post("/rag", response_model=schemas.RAGResponse)
# def rag_query(req: schemas.RAGRequest):
#     llm, emb = get_llm_and_emb()
#     col = get_collection()

#     q_emb = emb.embed_query(req.query)
#     # ask chroma for docs + distances
#     res = col.query(query_embeddings=[q_emb], n_results=req.k, include=["documents","distances","metadatas"])
#     # normalize shapes: most servers return nested lists
#     docs = res.get("documents", [[]])[0]
#     dists = res.get("distances", [[]])[0] if "distances" in res else None

#     if not docs:
#         raise HTTPException(status_code=404, detail="No documents found in vector DB. Run ingestion.")

#     # assemble prompt
#     context = "\n\n---\n\n".join(docs)
#     prompt = f"""You are an assistant that answers questions about the SQL schema.
# Use ONLY the documentation below. If answer not present, say "I don't know".

# Documentation:
# {context}

# Question: {req.query}

# Answer:"""
#     resp = llm.invoke(prompt)
#     answer = getattr(resp, "content", None) or str(resp)
#     sources = docs
#     return {"answer": answer, "sources": sources}

@app.post("/rag", response_model=schemas.RAGResponse)
def rag_query(req: schemas.RAGRequest):
    llm, emb = get_llm_and_emb()
    col = get_collection()

    # ---------------------------
    # 1) Retrieve documents (RAG)
    # ---------------------------
    q_emb = emb.embed_query(req.query)
    res = col.query(
        query_embeddings=[q_emb],
        n_results=req.k,
        include=["documents", "distances", "metadatas"]
    )

    docs = res.get("documents", [[]])[0]
    if not docs:
        raise HTTPException(status_code=404, detail="No documents in vector DB. Run ingestion.")

    context = "\n\n---\n\n".join(docs)

    # -------------------------------------------------------
    # 2) Decide whether question requires SQL or pure RAG
    # -------------------------------------------------------
    classifier_prompt = f"""
    Decide if the user question requires executing an SQL query
    on the actual database values.

    Return ONLY:
    - "sql" → if question needs database data (prices, totals, counts, max/min...)
    - "rag" → if question can be answered from documentation only.

    User question: "{req.query}"

    Documentation:
    {context}

    Answer with ONLY one word: sql or rag
        """.strip()

    mode = llm.invoke(classifier_prompt).content.strip().lower()

    # -------------------------------------------------------
    # 3) SQL MODE (dynamic SQL generation + execution)
    # -------------------------------------------------------
    if mode == "sql":

        sql_prompt = f"""
        You are an expert SQL generator.

        Write a SINGLE SQL SELECT query that answers the question:
        "{req.query}"

        REQUIREMENTS:
        - Must be a SELECT statement ONLY.
        - Must return useful column names (e.g., "price" instead of MAX(p.price)).
        - If the question asks for "most", "highest", "largest", use ORDER BY ... DESC LIMIT 1.
        - NO markdown, NO explanation, ONLY pure SQL.

        Schema documentation:
        {context}
                """.strip()

        sql_text = llm.invoke(sql_prompt).content.strip()

        # Remove fenced code blocks, if any
        if sql_text.startswith("```"):
            sql_text = "\n".join(sql_text.splitlines()[1:-1]).strip()

        sql_text = sql_text.strip()

        # Basic safety: only allow SELECT
        if not sql_text.lower().startswith("select"):
            return {
                "answer": f"Rejected unsafe SQL (not SELECT): {sql_text}",
                "sources": [sql_text]
            }

        # Try executing SQL
        try:
            rows = dbmod.run_query(sql_text)

            # If SELECT returned rows, normalize weird column names
            if isinstance(rows, list) and rows:
                row = rows[0]

                # Normalize column named like "MAX(price)" → "price"
                new_row = {}
                for k, v in row.items():
                    clean_key = k.lower()
                    if "(" in clean_key and ")" in clean_key:
                        clean_key = clean_key.replace("max(", "").replace("avg(", "").replace("min(", "").replace("sum(", "").replace(")", "")
                    new_row[clean_key] = v

                return {
                    "answer": new_row,
                    "sources": [sql_text]
                }

            return {"answer": rows, "sources": [sql_text]}

        except Exception as e:
            return {
                "answer": f"SQL error: {str(e)}",
                "sources": [sql_text]
            }

    # -------------------------------------------------------
    # 4) RAG MODE
    # -------------------------------------------------------
    prompt = f"""
    You are an assistant that answers questions about the SQL schema.
    Use ONLY the documentation below. If answer not present, say "I don't know".

    Documentation:
    {context}

    Question: {req.query}

    Answer:"""

    resp = llm.invoke(prompt)
    answer = getattr(resp, "content", None) or str(resp)

    return {
        "answer": answer,
        "sources": docs
    }


@app.post("/ingest")
def ingest_endpoint():
    # call your existing rag.ingest script programmatically
    from rag import ingest as rag_ingest
    try:
        rag_ingest.ingest()
        return {"status":"ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


### Adding elements to data
@app.post("/create_customer")
def create_customer(cust: schemas.CustomerCreate):
    sql = """
    INSERT INTO customers (name, email, country)
    VALUES (?, ?, ?)
    """
    params = [cust.name, cust.email, cust.country]
    try:
        result = dbmod.run_exec(sql, params)
        return {
            "status": "success",
            "inserted": cust,
            "rows_affected": result["rows_affected"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/create_product")
def create_product(prod: schemas.ProductCreate):
    sql = """
    INSERT INTO products (name, price)
    VALUES (?, ?)
    """
    params = [prod.name, prod.price]
    try:
        result = dbmod.run_exec(sql, params)
        return {
            "status": "success",
            "inserted": prod,
            "rows_affected": result["rows_affected"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/create_order")
def create_order(order: schemas.OrderCreate):
    sql = """
    INSERT INTO orders (customer_id, order_date)
    VALUES (?, ?)
    """
    params = [order.customer_id, order.order_date]
    try:
        result = dbmod.run_exec(sql, params)
        return {
            "status": "success",
            "inserted": order,
            "rows_affected": result["rows_affected"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/create_order_item")
def create_order_item(item: schemas.OrderItemCreate):
    sql = """
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES (?, ?, ?, ?)
    """
    params = [item.order_id, item.product_id, item.quantity, item.unit_price]
    try:
        result = dbmod.run_exec(sql, params)
        return {
            "status": "success",
            "inserted": item,
            "rows_affected": result["rows_affected"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))