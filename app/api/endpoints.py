import os
import time
import datetime
from flask import request
from flask_restx import Resource, Namespace, fields, reqparse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from database.mongo_client import insert_pdf_record, insert_log_record, get_log_records
from utils.pdf_processor import process_pdf
from utils.embeddings import get_embeddings_model
from langchain_chroma import Chroma

# Create namespaces
pdf_ns = Namespace('pdf', description='PDF upload operations')
query_ns = Namespace('query', description='Query operations')
logs_ns = Namespace('logs', description='Log operations')

# Define parsers for Swagger UI
pdf_upload_parser = reqparse.RequestParser()
pdf_upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='PDF file to upload')

query_parser = reqparse.RequestParser()
query_parser.add_argument('question', location='form', type=str, required=True, help='Question to ask about the documents')

# Define models
pdf_response_model = pdf_ns.model('PDFResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Response data')
})

query_response_model = query_ns.model('QueryResponse', {
    'answer': fields.String(description='Answer to the question'),
    'pdf_name': fields.String(description='Name of the PDF document'),
    'citations': fields.List(fields.Raw, description='Citations from the document')
})

logs_response_model = logs_ns.model('LogsResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Response message'),
    'logs': fields.List(fields.Raw, description='Log records'),
    'x_fields': fields.String(description='X-FIELDS header value', required=False)
})

logs_parser = reqparse.RequestParser()
logs_parser.add_argument('log_id', location='args', type=str, required=False, help='Log ID to filter logs')

@pdf_ns.route('/papers')
class PDFUpload(Resource):
    @pdf_ns.expect(pdf_upload_parser)
    @pdf_ns.marshal_with(pdf_response_model)
    def post(self):
        try:
            # Get file directly from request (more reliable than parser)
            file = request.files.get('file')
            
            if not file:
                return {'success': False, 'message': 'No file provided', 'data': None}, 400
            
            if not file.filename.lower().endswith('.pdf'):
                return {'success': False, 'message': 'Only PDF files are allowed', 'data': None}, 400
            
            # Save file
            filename = secure_filename(file.filename)
            storage_dir = os.getenv('PDF_STORAGE_DIR', '/app/storage/pdfs')
            os.makedirs(storage_dir, exist_ok=True)
            filepath = os.path.join(storage_dir, filename)
            file.save(filepath)
            
            # Process PDF and store in ChromaDB
            chroma_dir = os.getenv('CHROMA_STORAGE_DIR', '/app/storage/chroma')
            chunk_count = process_pdf(filepath, chroma_dir)
            
            # Store metadata in MongoDB
            record_id = insert_pdf_record({
                'filename': filename,
                'filepath': filepath,
                'chunks': chunk_count,
                'upload_time': datetime.datetime.utcnow().isoformat()
            })

            insert_log_record({
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'endpoint': '/pdf/papers',
                'method': 'POST',
                'status_code': 200,
                'message': 'PDF uploaded and indexed',
                'additional_data': {
                    'filename': file.filename,
                    'record_id': record_id,
                    'chunks': chunk_count
                }
            })

            return {
                'success': True,
                'message': 'PDF uploaded and embedded successfully',
                'data': {
                    'record_id': record_id,
                    'chunks_processed': chunk_count
                }
            }, 200
            
        except Exception as e:
            insert_log_record({
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'endpoint': '/pdf/papers',
                'method': 'POST',
                'status_code': 500,
                'message': f'Error processing PDF: {str(e)}',
                'additional_data': {}
            })
            return {'success': False, 'message': f'Error processing PDF: {str(e)}', 'data': None}, 500


@query_ns.route('/')
class Query(Resource):
    @query_ns.expect(query_parser)
    @query_ns.marshal_with(query_response_model)
    def post(self):
        try:
            # Parse the question using the parser
            args = query_parser.parse_args()
            question = args['question']
            
            if not question or not question.strip():
                insert_log_record({
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'endpoint': '/query/',
                    'method': 'POST',
                    'status_code': 400,
                    'message': 'Missing question',
                    'additional_data': {}
                })
                return {
                    'answer': 'Please provide a question.',
                    'pdf_name': '',
                    'citations': []
                }, 400

            # Get list of available documents from ChromaDB
            from utils.embeddings import get_embeddings_model
            from langchain_chroma import Chroma
            
            embedding_model = get_embeddings_model()
            chroma_dir = os.getenv('CHROMA_STORAGE_DIR', '/app/storage/chroma')
            vectorstore = Chroma(
                collection_name="pdf_chunks",
                embedding_function=embedding_model,
                persist_directory=chroma_dir
            )
            
            # Get all documents and their names
            chroma_data = vectorstore.get()
            available_documents = set()
            
            for metadata in chroma_data.get("metadatas", []):
                if metadata and "document_name" in metadata:
                    available_documents.add(metadata["document_name"])
            
            # Check if question mentions any document name
            question_lower = question.lower()
            mentioned_documents = []
            
            for doc_name in available_documents:
                doc_name_lower = doc_name.lower()
                # Remove file extension for comparison
                doc_name_without_ext = doc_name_lower.replace('.pdf', '').replace('.txt', '')
                
                if (doc_name_lower in question_lower or 
                    doc_name_without_ext in question_lower or
                    doc_name_without_ext.replace('_', ' ') in question_lower or
                    doc_name_without_ext.replace('-', ' ') in question_lower):
                    mentioned_documents.append(doc_name)
            
            # Validation: Require at least one document to be mentioned
            if not mentioned_documents:
                error_message = f"Please specify which document you're asking about. Available documents: {', '.join(available_documents)}"
                
                insert_log_record({
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'endpoint': '/query/',
                    'method': 'POST',
                    'status_code': 400,
                    'message': 'No document specified in question',
                    'additional_data': {
                        'question': question,
                        'available_documents': list(available_documents),
                        'error': 'Document name not mentioned in question'
                    }
                })
                
                return {
                    'answer': error_message,
                    'pdf_name': '',
                    'citations': []
                }, 400

            start_time = time.time()
            
            # Get detailed information from the chain
            from rag.chain import run_query_chain_with_details
            result, retrieved_chunks, processing_metadata = run_query_chain_with_details(question, mentioned_documents[0])
            
            processing_time = time.time() - start_time

            # Prepare detailed logging data
            log_data = {
                'question': question,
                'answer': result.get('answer', ''),
                'citations': result.get('citations', []),
                'processing_time': processing_time,
                'mentioned_documents': mentioned_documents,
                'available_documents': list(available_documents),
                'retrieved_chunks': [
                    {
                        'content': chunk.page_content[:200] + '...' if len(chunk.page_content) > 200 else chunk.page_content,
                        'metadata': chunk.metadata,
                        'document_name': chunk.metadata.get('document_name', ''),
                        'chunk_id': chunk.metadata.get('chunk_id', '')
                    }
                    for chunk in retrieved_chunks
                ],
                'performance_metrics': {
                    'total_processing_time': processing_time,
                    'chunks_retrieved': len(retrieved_chunks),
                    'model_response_time': processing_metadata.get('model_response_time', 0),
                    'retrieval_time': processing_metadata.get('retrieval_time', 0)
                },
                'source_citations': [
                    {
                        'document_name': citation.get('document_name', ''),
                        'chunk_id': citation.get('chunk_id', ''),
                        'page': citation.get('page', ''),
                        'confidence': citation.get('confidence', 1.0)
                    }
                    for citation in result.get('citations', [])
                ]
            }

            insert_log_record({
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'endpoint': '/query/',
                'method': 'POST',
                'status_code': 200,
                'message': 'Query executed successfully',
                'additional_data': log_data
            })

            raw_citations = result.get("citations", [])
            formatted_citations = []
            if isinstance(raw_citations, list):
                for c in raw_citations:
                    if isinstance(c, dict):
                        formatted_citations.append({
                            "document_name": c.get("document_name", ""),
                            "chunk_id": c.get("chunk_id", "")
                        })

            response_data = {
                'answer': str(result.get('answer', '')),
                'pdf_name': mentioned_documents[0] if mentioned_documents else 'context',
                'citations': formatted_citations
            }
            
            return response_data, 200
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            insert_log_record({
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'endpoint': '/query/',
                'method': 'POST',
                'status_code': 500,
                'message': f'Error processing query: {str(e)}',
                'additional_data': {}
            })
            return {
                'answer': f'Error processing the question: {str(e)}',
                'pdf_name': '',
                'citations': []
            }, 500


@logs_ns.route('/')
class Logs(Resource):
    @logs_ns.expect(logs_parser)
    def get(self):
        try:
            args = logs_parser.parse_args()
            log_id = args.get('log_id')
            logs = get_log_records()
            if log_id:
                logs = [log for log in logs if str(log.get('record_id') or log.get('log_id') or log.get('id')) == log_id]
            insert_log_record({
                'timestamp': datetime.datetime.utcnow().isoformat(),
                'endpoint': '/logs/',
                'method': 'GET',
                'status_code': 200,
                'message': 'Log records fetched',
                'additional_data': {
                    'count': len(logs)
                }
            })
            return {
                'success': True,
                'message': 'Log records retrieved',
                'logs': logs
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching logs: {str(e)}',
                'logs': []
            }, 500


def register_routes(api):
    api.add_namespace(pdf_ns)
    api.add_namespace(query_ns)
    api.add_namespace(logs_ns)
