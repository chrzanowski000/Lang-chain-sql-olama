# rag/query.py
import os
from dotenv import load_dotenv
load_dotenv()

from chromadb import HttpClient
from langchain_ollama import ChatOllama, OllamaEmbeddings

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000


def get_collection():
    client = HttpClient(
        host="localhost",
        port=8000,
        tenant="default_tenant",
        database="default_db"
    )

    return client.get_collection("docs")


def retrieve_docs(col, emb_model, query, k=4):
    q_emb = emb_model.embed_query(query)

    res = col.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["documents", "distances"]
    )

    documents = res.get("documents", [[]])[0]
    distances = res.get("distances", [[]])[0]

    return documents, distances


def interactive():
    llm = ChatOllama(model="llama3:8b", temperature=0.0)
    emb = OllamaEmbeddings(model="llama3:8b")

    col = get_collection()

    print("Local RAG ready. Type 'exit' to quit.")

    while True:
        q = input("\nQuestion> ").strip()
        if q.lower() in ("exit", "quit"):
            break
        if not q:
            continue

        docs, dists = retrieve_docs(col, emb, q)
        if not docs:
            print("No relevant docs found.")
            continue

        print("\nRetrieved chunks:")
        for i, d in enumerate(docs):
            print(f"--- chunk {i} (dist={round(dists[i],4)}) ---\n{d[:500]}\n")

        context = "\n\n---\n\n".join(docs)

        prompt = f"""
Use ONLY the following documentation to answer the question.
If the answer is not in the documentation, say "I don't know".

DOCUMENTATION:
{context}

QUESTION: {q}

ANSWER:
"""

        resp = llm.invoke(prompt)
        print("\nAnswer:\n", resp.content)


if __name__ == "__main__":
    interactive()
