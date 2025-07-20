import os
from langchain_ollama import OllamaEmbeddings

def get_embeddings_model():
    """
    Initialize and return Ollama embeddings model
    """
    ollama_host = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
    embedding_model = os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
    
    return OllamaEmbeddings(
        model=embedding_model,
        base_url=ollama_host
    )
