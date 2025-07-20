import os
from pymongo import MongoClient
from datetime import datetime
import json

def init_mongo():
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DATABASE", "pdf_upload_db")
    client = MongoClient(mongo_uri)
    return client[db_name]

def insert_pdf_record(data):
    db = init_mongo()
    return str(db.pdfs.insert_one(data).inserted_id)

def insert_log_record(data):
    db = init_mongo()

    # Ensure timestamp is properly formatted
    if 'timestamp' in data and isinstance(data['timestamp'], datetime):
        data['timestamp'] = data['timestamp'].isoformat()
    
    # Clean and validate the data
    clean_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Truncate very long strings to prevent MongoDB issues
            clean_data[key] = value[:10000] if len(value) > 10000 else value
        else:
            clean_data[key] = value

    # Insert into logs collection (not query_logs)
    db.logs.insert_one(clean_data)

def get_log_records():
    db = init_mongo()
    
    # Get logs from both collections
    logs_from_logs = list(db.logs.find({}, {'_id': False}).sort('timestamp', -1).limit(50))
    logs_from_query_logs = list(db.query_logs.find({}, {'_id': False}).sort('timestamp', -1).limit(50))
    
    # Combine and sort all logs
    all_logs = logs_from_logs + logs_from_query_logs
    
    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Limit to 100 most recent logs
    all_logs = all_logs[:100]
    
    for log in all_logs:
        if 'timestamp' in log and isinstance(log['timestamp'], datetime):
            log['timestamp'] = log['timestamp'].isoformat()

    return all_logs
