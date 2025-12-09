# api/main.py
import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from typing import List

load_dotenv()
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

# Initialize LLM/emb client lazily (so server starts fast)
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

@app.post("/rag", response_model=schemas.RAGResponse)
def rag_query(req: schemas.RAGRequest):
    llm, emb = get_llm_and_emb()
    col = get_collection()

    q_emb = emb.embed_query(req.query)
    # ask chroma for docs + distances
    res = col.query(query_embeddings=[q_emb], n_results=req.k, include=["documents","distances","metadatas"])
    # normalize shapes: most servers return nested lists
    docs = res.get("documents", [[]])[0]
    dists = res.get("distances", [[]])[0] if "distances" in res else None

    if not docs:
        raise HTTPException(status_code=404, detail="No documents found in vector DB. Run ingestion.")

    # assemble prompt
    context = "\n\n---\n\n".join(docs)
    prompt = f"""You are an assistant that answers questions about the SQL schema.
Use ONLY the documentation below. If answer not present, say "I don't know".

Documentation:
{context}

Question: {req.query}

Answer:"""
    resp = llm.invoke(prompt)
    answer = getattr(resp, "content", None) or str(resp)
    sources = docs
    return {"answer": answer, "sources": sources}

@app.post("/ingest")
def ingest_endpoint():
    # call your existing rag.ingest script programmatically
    from rag import ingest as rag_ingest
    try:
        rag_ingest.ingest()
        return {"status":"ingested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
