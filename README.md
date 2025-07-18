# Academic PDF Question Answering AI Agent

## Description
A Flask-based AI agent that uses RAG with Ollama and ChromaDB to answer questions based on uploaded academic PDF documents.

## Technologies
- Python Flask
- Docker & Docker Compose
- ChromaDB
- MongoDB
- Ollama
- Pydantic
- Swagger UI

## Running the App
1. `docker-compose up --build`
2. Access the API at `http://localhost:5000/swagger/`

## Endpoints
- `POST /pdf/papers`: Upload PDFs
- `GET /pdf/files`: List uploaded PDFs
- `POST /query`: Ask a question
- `GET /logs/application`: View application logs