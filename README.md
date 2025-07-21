# Academic Paper Query API

A Flask-based RAG (Retrieval-Augmented Generation) API for querying academic papers using Ollama and ChromaDB.

## 🚀 Features

- **PDF Upload & Processing**: Upload academic papers and automatically chunk them
- **RAG-powered Queries**: Ask questions about uploaded documents using AI
- **Vector Search**: Fast semantic search using ChromaDB
- **Detailed Logging**: Comprehensive logging of all operations
- **Swagger UI**: Interactive API documentation


## 🚀 Quick Start


1. **Start the services**
   - docker-compose up -d
   - docker-compose up --build

3. **Access the API**
   - Swagger UI: http://localhost:5000/swagger/
   - API Base URL: http://localhost:5000

## 📚 API Endpoints

### 1. Upload PDF
- **POST** `/pdf/papers`
- Upload academic papers for processing
- Supports PDF files only

### 2. Query Documents
- **POST** `/query/`
- Ask questions about uploaded documents
- Validation- Requires document name in question

### 3. View Logs
- **GET** `/logs/`
- View detailed operation logs

## 🔧 Configuration

### Environment Variables

### Model Configuration
The system uses the `academiqa` model based on Ollama with custom academic prompts.

## 📊 Monitoring

### Health Checks
- Ollama: Automatic health check every 30s
- MongoDB: Standard container health monitoring
- ChromaDB: Built-in health monitoring

### Logging
All operations are logged to MongoDB with detailed metadata:
- Query processing time
- Retrieved chunks
- Model response metrics
- Error tracking

### 4. File Constracture
docker-master/
├── app/
│   ├── api/
│   │   ├── endpoints.py      # API endpoints
│   │   └── swagger.py        # Swagger configuration
│   ├── database/
│   │   ├── mongo_client.py   # MongoDB connection
│   │   └── chroma_client.py  # ChromaDB connection
│   ├── rag/
│   │   ├── chain.py          # RAG chain implementation
│   │   ├── prompt_templates.py
│   │   └── output_parser.py
│   ├── utils/
│   │   ├── embeddings.py     # Embeddings configuration
│   │   └── pdf_processor.py  # PDF processing
│   ├── config.py             # Application configuration
│   └── main.py               # Flask application
├── modelfile/
│   └── Modelfile             # Ollama model configuration
│   └── start_ollama.sh
├── docker-compose.yml        # Docker services
├── Dockerfile                # Flask app container
└── requirements.txt          # Python dependencies

### Version Locking
All dependencies are locked to specific versions to ensure reproducibility:
- Python packages: Exact versions in `requirements.txt`
- Docker images: Tagged versions in `docker-compose.yml`
- Base images: Specific Python version in `Dockerfile`

## 📝 License

This project is licensed under the MIT License.