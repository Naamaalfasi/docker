from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os

client = None
db = None

def init_mongo():
    global client, db
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    mongo_db = os.getenv('MONGODB_DATABASE', 'pdf_upload_db')
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    return db

def insert_pdf_record(data):
    return str(db.pdf_files.insert_one(data).inserted_id)

def log_query(question, result):
    db.query_logs.insert_one({
        'timestamp': datetime.utcnow(),
        'question': question,
        'answer': result['answer'],
        'citations': result['citations']
    })

def get_log_records():
    return list(db.query_logs.find({}, {'_id': 0}))