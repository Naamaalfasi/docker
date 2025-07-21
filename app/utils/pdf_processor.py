import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from utils.embeddings import get_embeddings_model
from datetime import datetime

def process_pdf(file_path: str, chroma_dir: str = None) -> int:
    """
    Process a PDF file and store chunks in ChromaDB
    """
    try:
        # Load PDF
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(pages)
        
        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                'chunk_id': f"chunk_{i}",
                'document_name': os.path.basename(file_path),
                'upload_time': datetime.utcnow().isoformat(),
                'creation_date': str(pages[0].metadata.get('creation_date', 'Unknown')),
                'total_pages': len(pages)
            })
        
        # Initialize embeddings and vectorstore
        embedding_model = get_embeddings_model()
        
        if chroma_dir is None:
            chroma_dir = os.getenv('CHROMA_STORAGE_DIR', '/app/storage/chroma')
            
        vectorstore = Chroma(
            collection_name="pdf_chunks",
            embedding_function=embedding_model,
            persist_directory=chroma_dir
        )
        
        # Store chunks in ChromaDB
        vectorstore.add_documents(chunks)
        
        return len(chunks)
        
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")
