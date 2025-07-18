def get_prompt_template():
    return """You are an academic assistant. Answer the following question based only on the provided context.

Context:
{context}

Question:
{question}

Answer:"""