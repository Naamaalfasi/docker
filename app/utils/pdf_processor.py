import logging
from PyPDF2 import PdfReader
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.embeddings import get_embeddings_model

def processor_pdf(filepath, doc_id, original_filename, chroma_client):
        # Load PDF into LangChain Documents
        loader = PyPDFLoader(filepath)
        documents = loader.load()

        # Add metadata
        for doc in documents:
            doc.metadata["document_id"] = doc_id
            doc.metadata["document_name"] = original_filename
            doc.metadata["source"] = original_filename

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        # Embed and store in ChromaDB
        embedding_model = get_embeddings_model()
        chroma_client.add_documents(
            documents=chunks,
            embedding=embedding_model,
            ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
        )
        return len(chunks)
