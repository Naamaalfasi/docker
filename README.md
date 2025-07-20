# Academic Paper Query API

A Flask-based RAG (Retrieval-Augmented Generation) API for querying academic papers using Ollama and ChromaDB.

## 🚀 Features

- **PDF Upload & Processing**: Upload academic papers and automatically chunk them
- **RAG-powered Queries**: Ask questions about uploaded documents using AI
- **Vector Search**: Fast semantic search using ChromaDB
- **Detailed Logging**: Comprehensive logging of all operations
- **Swagger UI**: Interactive API documentation

## 📋 Prerequisites

- Docker and Docker Compose
- At least 8GB RAM (for Ollama models)
- 10GB free disk space

## 🛠️ Technology Stack

### Core Components
- **Python**: 3.10.13
- **Flask**: 3.0.0
- **Flask-RESTX**: 1.3.0
- **Ollama**: 0.1.29
- **ChromaDB**: 0.4.22
- **MongoDB**: 7.0.5

### AI/ML Libraries
- **LangChain**: 0.1.0
- **LangChain-Community**: 0.0.20
- **LangChain-Ollama**: 0.1.0
- **LangChain-Chroma**: 0.1.0

### Database & Storage
- **PyMongo**: 4.6.0
- **ChromaDB**: 0.4.22
- **MongoDB**: 7.0.5

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd docker-master
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

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
- Requires document name in question

### 3. View Logs
- **GET** `/logs/`
- View detailed operation logs

## 🔧 Configuration

### Environment Variables
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DATABASE`: Database name
- `OLLAMA_HOST`: Ollama service URL
- `CHROMA_HOST`: ChromaDB service URL
- `DEBUG`: Enable debug mode

### Model Configuration
The system uses the `academiqa` model based on `llama3:latest` with custom academic prompts.

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

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Model Not Found**
   ```bash
   docker exec docker-master-ollama-1 ollama list
   ```

2. **Memory Issues**
   - Ensure at least 8GB RAM available
   - Consider reducing model size

3. **Port Conflicts**
   - Check if ports 5000, 11434, 27017, 8000, 8081 are available

### Logs
```bash
# View Flask app logs
docker-compose logs flask-app

# View Ollama logs
docker-compose logs ollama

# View all logs
docker-compose logs
```

## 🔄 Updates

### Updating Dependencies
1. Update version numbers in `requirements.txt`
2. Update Docker images in `docker-compose.yml`
3. Rebuild containers: `docker-compose build --no-cache`

### Version Locking
All dependencies are locked to specific versions to ensure reproducibility:
- Python packages: Exact versions in `requirements.txt`
- Docker images: Tagged versions in `docker-compose.yml`
- Base images: Specific Python version in `Dockerfile`

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue with detailed information