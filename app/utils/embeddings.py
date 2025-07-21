import os
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings_model():
    """
    Initialize and return HuggingFace embeddings model
    """
    model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    
    print(f"DEBUG: Using embedding model: {model_name}")
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'}
    )
