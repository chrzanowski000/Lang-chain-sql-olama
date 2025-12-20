
import os
from dotenv import load_dotenv
load_dotenv()

from chromadb import HttpClient
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE = os.path.dirname(os.path.dirname(__file__))
DOCS_PATH = os.path.join(BASE, "docs")

CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", 8000))
CHROMA_TENANT = os.environ.get("CHROMA_TENANT", "default_tenant")
CHROMA_DB = os.environ.get("CHROMA_DATABASE", "default_database")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:8b")


def ingest():
    print("Loading docs...")
    loader = DirectoryLoader(DOCS_PATH, glob="**/*.md", loader_cls=TextLoader)
    docs = loader.load()
    print(f"Loaded {len(docs)} docs")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    splits = splitter.split_documents(docs)
    print(f"Split into {len(splits)} chunks")

    emb = OllamaEmbeddings(model="llama3:8b")

    print("Connecting to Chroma server at localhost:8000 ...")
    client = HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        tenant=CHROMA_TENANT,
        database=CHROMA_DB
    )

    try:
        col = client.get_collection("docs")
        print("Using existing collection")
    except:
        col = client.create_collection("docs", metadata={"hnsw:space": "cosine"})
        print("Created new collection")

    texts = [d.page_content for d in splits]
    metadatas = [d.metadata or {} for d in splits]
    ids = [f"doc_{i}" for i in range(len(texts))]

    print("Computing embeddings...")
    embs = emb.embed_documents(texts)

    print("Adding to Chroma collection via upsert...")
    col.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embs
    )

    print("Ingestion complete! Data is now stored inside the Chroma server.")


if __name__ == "__main__":
    ingest()
