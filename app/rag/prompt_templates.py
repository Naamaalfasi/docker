from langchain_core.prompts import PromptTemplate

def get_prompt_template():
    return PromptTemplate(
        input_variables=["context", "input", "document_name"],
        template="""
You are an academic assistant analyzing the document \"{document_name}\".

Answer the question based ONLY on the content provided in the context below. The context contains relevant excerpts from the document \"{document_name}\".

IMPORTANT:
- You are specifically analyzing the document \"{document_name}\"
- Base your answer ONLY on the provided context
- If the question asks for the first line, first sentence, or similar, try to extract and return ONLY the first line or sentence from the context if it exists. If you cannot find it in the context, clearly state that the information is not available.
- If the question asks about this specific document, refer to it by name
- If the information in the context is not sufficient to answer the question, clearly state this
- Provide a detailed and accurate answer

Document being analyzed: {document_name}

Context from the document:
{context}

Question:
{input}

Answer:
"""
    )
