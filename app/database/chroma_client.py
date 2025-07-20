from langchain_chroma import Chroma
from utils.embeddings import get_embeddings_model

def init_chroma():
    embedding_model = get_embeddings_model()
    return Chroma(
        collection_name="pdf_chunks",
        embedding_function=embedding_model,
        persist_directory="/app/storage/chroma"
    )

