from flask_restx import Api
from app.api.endpoints import api_ns

api = Api(
    title="Academic QA API",
    version="1.0",
    description="Upload academic PDFs and query them using RAG with Ollama",
    doc="/docs"
)

api.add_namespace(api_ns)
