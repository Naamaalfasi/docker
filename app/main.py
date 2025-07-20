from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from api.endpoints import register_routes
from database.mongo_client import init_mongo
from database.chroma_client import init_chroma
import os

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    try:
        # Test database connections
        from database.mongo_client import init_mongo
        from database.chroma_client import init_chroma
        
        mongo_db = init_mongo()
        chroma_client = init_chroma()
        
        # Test ChromaDB connection
        chroma_client.heartbeat()
        
    except Exception as e:
        pass  # Continue even if databases are not available during startup

    api = Api(app, version='1.0', title='Academic Paper Query API',
              description='A Flask API for querying academic papers using RAG with Ollama',
              doc='/swagger/')

    register_routes(api)
    
    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.getenv('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
