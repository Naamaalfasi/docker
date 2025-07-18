from langchain.chains import RetrievalQA
from langchain_ollama import Ollama
from app.utils.embeddings import get_embeddings_model
from app.rag.prompt_templates import get_rag_prompt_template
from app.rag.output_parser import QueryOutputParser
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from app.database.chroma_client import init_chroma
from langchain.vectorstores.chroma import Chroma
from langchain.schema import Document

chroma_collection = init_chroma()

def run_query_chain(question: str):
    # Initialize embedding model and retriever
    embedding_model = get_embeddings_model()

    # Wrap ChromaDB collection with LangChain-compatible retriever
    vectorstore = Chroma(
        collection_name="pdf_chunks",
        embedding_function=embedding_model,
        collection=chroma_collection
    )

    base_retriever = vectorstore.as_retriever()
    compression = EmbeddingsFilter(embeddings=embedding_model, similarity_threshold=0.5)
    retriever = ContextualCompressionRetriever(
        base_compressor=compression,
        base_retriever=base_retriever
    )

    # Load model
    llm = Ollama(model="academiqa")

    # Build QA chain
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": get_rag_prompt_template()
        }
    )

    result = rag_chain({"query": question})
    return QueryOutputParser().parse(result)
