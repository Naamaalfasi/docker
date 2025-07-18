from flask_restx import Api, Resource, Namespace, fields, reqparse
from flask import request, current_app
from werkzeug.datastructures import FileStorage
from app.utils.pdf_processor import processor_pdf
from app.models import QueryRequest, QueryResponse
from app.rag.chain import get_answer_from_query
from app.database.mongo_client import log_query
import os
import uuid


api = Api(
    title='AI Agent API',
    version='1.0',
    description='API for PDF upload and academic question answering',
    doc='/swagger/'
)

pdf_ns = Namespace('pdf', description='PDF operations')
logs_ns = Namespace('logs', description='Application logs')
query_ns = Namespace('query', description='Ask AI agent')

api.add_namespace(pdf_ns)
api.add_namespace(logs_ns)
api.add_namespace(query_ns)

pdf_upload_parser = reqparse.RequestParser()
pdf_upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='PDF file to upload')

pdf_response_model = api.model('PDFResponse', {
    'success': fields.Boolean,
    'message': fields.String,
    'data': fields.Raw
})

log_response_model = api.model('LogResponse', {
    'success': fields.Boolean,
    'message': fields.String,
    'logs': fields.List(fields.Raw)
})

query_response_model = api.model('QueryResponse', {
    'success': fields.Boolean,
    'answer': fields.String,
    'pdf_name': fields.String,
    'citations': fields.List(fields.Raw)
})

config = None
pdf_processor = None
db_manager = None
app_logger = None

@pdf_ns.route('/papers')
class PDFUpload(Resource):
    @pdf_ns.expect(pdf_upload_parser)
    @pdf_ns.marshal_with(pdf_response_model)
    def post(self):
        file = request.files.get('file')
        if not file or file.filename == '':
            return {'success': False, 'message': 'No file provided', 'data': None}, 400

        if not pdf_processor.allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            return {'success': False, 'message': 'Invalid file type', 'data': None}, 400

        filename = file.filename
        file_content = file.read()
        file.seek(0)

        text_content = pdf_processor.extract_text_from_pdf(io.BytesIO(file_content))

        pdf_data = {
            'filename': filename,
            'file_size': len(file_content),
            'upload_time': datetime.utcnow(),
            'content_text': text_content
        }

        record_id = db_manager.insert_pdf_record(pdf_data)

        return {
            'success': True,
            'message': 'PDF uploaded',
            'data': {
                'record_id': record_id,
                'filename': filename,
                'content_preview': text_content[:200] + '...'
            }
        }, 200

@query_ns.route('/')
class Query(Resource):
    @query_ns.expect(api.model('QueryInput', {
        'question': fields.String(required=True),
    }))
    @query_ns.marshal_with(query_response_model)
    def post(self):
        data = request.json
        question = data.get('question')
        if not question:
            return {'success': False, 'answer': '', 'pdf_name': '', 'citations': []}, 400

        result = run_query_chain(question)

        return {
            'success': True,
            'answer': result['answer'],
            'pdf_name': 'context',
            'citations': result['citations']
        }, 200

@logs_ns.route('/application')
class Logs(Resource):
    @logs_ns.marshal_with(log_response_model)
    def get(self):
        logs = db_manager.get_log_records()
        return {
            'success': True,
            'message': 'Log records retrieved',
            'logs': logs
        }, 200

# Dependency injection setup (to be used from main.py)
def init_dependencies(config_obj, db_mgr, processor, logger):
    global config, db_manager, pdf_processor, app_logger
    config = config_obj
    db_manager = db_mgr
    pdf_processor = processor
    app_logger = logger