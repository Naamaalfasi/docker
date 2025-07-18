from langchain_ollama.embeddings import OllamaEmbeddings

def generate_embeddings(documents):
    embedder = OllamaEmbeddings(model="nomic-embed-text")
    for doc in documents:
        doc.embedding = embedder.embed_query(doc.page_content)
    return documents
