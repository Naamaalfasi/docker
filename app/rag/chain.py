from utils.embeddings import get_embeddings_model
from rag.prompt_templates import get_prompt_template
from rag.output_parser import parse_llm_response
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os
import time

def run_query_chain(question: str, document_name: str = None):
    try:
        start_time = time.time()
        
        embedding_model = get_embeddings_model()

        chroma_dir = os.getenv('CHROMA_STORAGE_DIR', '/app/storage/chroma')
        vectorstore = Chroma(
            collection_name="pdf_chunks",
            embedding_function=embedding_model,
            persist_directory=chroma_dir
        )
        
        # Check if there are documents in ChromaDB
        chroma_data = vectorstore.get()
        document_count = len(chroma_data["documents"])
        
        if document_count == 0:
            return {
                "answer": "No documents available for querying. Please upload a PDF file first via /pdf/papers endpoint",
                "citations": []
            }

        # Use a simpler retriever with better performance
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Reduced from 5 to 3 for better performance
        )

        prompt_template = get_prompt_template()
        
        ollama_host = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'academiqa')
        
        llm = OllamaLLM(
            model=ollama_model, 
            base_url=ollama_host,
            timeout=120  # 2 minutes timeout
        )

        # Get retrieved documents
        retrieved_docs = retriever.invoke(question)
        
        if len(retrieved_docs) == 0:
            return {
                "answer": "No relevant information found for your question in the document. Try asking a different question or ensure the document contains relevant information.",
                "citations": []
            }

        # Format context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Create prompt with document name
        formatted_prompt = prompt_template.format(
            context=context,
            input=question,
            document_name=document_name or "the document"
        )
        
        result = llm.invoke(formatted_prompt)

        processing_time = time.time() - start_time

        parsed_result = parse_llm_response(result)
        
        return parsed_result
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "answer": f"Error processing the question: {str(e)}",
            "citations": []
        }

def run_query_chain_with_details(question: str, document_name: str = None):
    """
    Enhanced version that returns detailed information for logging
    """
    try:
        start_time = time.time()
        
        embedding_model = get_embeddings_model()

        chroma_dir = os.getenv('CHROMA_STORAGE_DIR', '/app/storage/chroma')
        vectorstore = Chroma(
            collection_name="pdf_chunks",
            embedding_function=embedding_model,
            persist_directory=chroma_dir
        )
        
        # Check if there are documents in ChromaDB
        chroma_data = vectorstore.get()
        document_count = len(chroma_data["documents"])
        
        if document_count == 0:
            return {
                "answer": "No documents available for querying. Please upload a PDF file first via /pdf/papers endpoint",
                "citations": []
            }, [], {}

        # Use a simpler retriever with better performance
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        prompt_template = get_prompt_template()
        
        ollama_host = os.getenv('OLLAMA_HOST', 'http://ollama:11434')
        ollama_model = os.getenv('OLLAMA_MODEL', 'academiqa')
        
        llm = OllamaLLM(
            model=ollama_model, 
            base_url=ollama_host,
            timeout=120
        )
        
        # Get retrieved documents with timing
        retrieval_start = time.time()
        retrieved_docs = retriever.invoke(question)
        retrieval_time = time.time() - retrieval_start
        
        if len(retrieved_docs) == 0:
            return {
                "answer": "No relevant information found for your question in the document. Try asking a different question or ensure the document contains relevant information.",
                "citations": []
            }, [], {}

        # Format context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Create prompt with document name
        formatted_prompt = prompt_template.format(
            context=context,
            input=question,
            document_name=document_name or "the document"
        )

        # Generate answer with timing
        model_start = time.time()
        result = llm.invoke(formatted_prompt)
        model_response_time = time.time() - model_start

        processing_time = time.time() - start_time

        # Prepare processing metadata
        processing_metadata = {
            'total_processing_time': processing_time,
            'retrieval_time': retrieval_time,
            'model_response_time': model_response_time,
            'chunks_retrieved': len(retrieved_docs),
            'total_documents_in_db': document_count,
            'document_name': document_name
        }

        parsed_result = parse_llm_response(result)
        
        return parsed_result, retrieved_docs, processing_metadata
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "answer": f"Error processing the question: {str(e)}",
            "citations": []
        }, [], {}
