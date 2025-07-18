import chromadb
from chromadb.config import Settings

_collection = None

def init_chroma():
    global _collection
    client = chromadb.Client(Settings(
        chroma_api_impl="rest",
        chroma_server_host=os.getenv("CHROMA_HOST", "localhost"),
        chroma_server_http_port=8000
    ))
    _collection = client.get_or_create_collection("pdf_chunks")
    return _collection
