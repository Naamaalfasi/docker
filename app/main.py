from flask import Flask
from flask_restx import Api
from app.database.mongo_client import init_mongo
from app.database.chroma_client import init_chroma
from app.api.endpoints import register_routes
from app.api.swagger import configure_swagger

def create_app():
    app = Flask(__name__)
    app.config['CHROMA_CLIENT'] = init_chroma()
    app.config['MONGO_CLIENT'] = init_mongo()

    api = Api(app, version='1.0', title='Academic Paper Query API', description='RAG-powered API for querying academic papers')

    register_routes(api)
    configure_swagger(api)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
