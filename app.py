from flask import Flask, request, jsonify
from functools import wraps
import os
from pinecone_client import PineconeClient
from embedding_client import QwenEmbedding
import logging

app = Flask(__name__)

# CORS support
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/', methods=['OPTIONS'])
@app.route('/retrieval', methods=['OPTIONS'])
def handle_options():
    return '', 204
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize clients
try:
    pc_client = PineconeClient(
        api_key=os.getenv('PINECONE_API_KEY'),
        host=os.getenv('PINECONE_HOST'),
        index_name=os.getenv('PINECONE_INDEX_NAME', 'dify-knowledge')
    )
    logger.info("Pinecone client initialized")
except Exception as e:
    logger.error(f"Failed to init Pinecone: {e}")
    pc_client = None

try:
    embedder = QwenEmbedding(api_key=os.getenv('QWEN_API_KEY'))
    logger.info("Qwen Embedding client initialized")
except Exception as e:
    logger.error(f"Failed to init Qwen Embedding: {e}")
    embedder = None

# API auth decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Invalid authorization header'}), 401

        token = auth_header.split(' ')[1]
        if token != os.getenv('DIFY_API_KEY', 'dify_external_kb_secret_key_2026'):
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated

@app.route('/retrieval', methods=['GET', 'POST'])
@require_auth
def retrieval():
    # Handle GET for Dify Cloud's initial check
    if request.method == 'GET':
        return jsonify({
            'message': 'External Knowledge Base API is ready',
            'endpoints': {
                'retrieval': 'POST /retrieval - Perform semantic search',
                'health': 'GET /health - Health check'
            }
        })

    # POST request for actual retrieval
    """Dify external knowledge base retrieval endpoint"""
    if not embedder or not pc_client:
        return jsonify({'error': 'Service not properly initialized'}), 500

    try:
        # Handle various Content-Type formats
        content_type = request.headers.get('Content-Type', '')
        logger.info(f"Request Content-Type: {content_type}")

        # Try to get JSON data, handling different content types
        data = request.get_json(force=True, silent=True)
        if data is None:
            # Try parsing manually if get_json fails
            import json
            data = json.loads(request.data.decode('utf-8'))

        knowledge_id = data.get('knowledge_id')
        query = data.get('query')
        retrieval_setting = data.get('retrieval_setting', {})
        top_k = retrieval_setting.get('top_k', 3)
        score_threshold = retrieval_setting.get('score_threshold', 0.5)

        logger.info(f"Query: knowledge_id={knowledge_id}, query={query[:50] if query else 'None'}..., top_k={top_k}")

        query_vector = embedder.embed_text(query)
        logger.info(f"Generated embedding: dim={len(query_vector)}")

        query_filter = {'knowledge_id': knowledge_id} if knowledge_id else None

        results = pc_client.query(
            vector=query_vector,
            top_k=top_k,
            filter=query_filter
        )

        records = []
        for match in results.get('matches', []):
            score = float(match.get('score', 0))
            if score >= score_threshold:
                metadata = match.get('metadata', {})
                records.append({
                    'content': metadata.get('content', ''),
                    'score': score,
                    'title': metadata.get('title', ''),
                    'metadata': {
                        'path': metadata.get('path', ''),
                        'description': metadata.get('description', '')
                    }
                })

        logger.info(f"Found {len(records)} records above threshold {score_threshold}")
        return jsonify({'records': records})

    except Exception as e:
        logger.error(f"Error in retrieval: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'pinecone': pc_client is not None,
        'embedding': embedder is not None
    })

@app.route('/admin/upload', methods=['POST'])
def upload_document():
    """Upload document to Pinecone (for testing)"""
    if not embedder or not pc_client:
        return jsonify({'error': 'Service not properly initialized'}), 500

    try:
        # Handle various Content-Type formats
        data = request.get_json(force=True, silent=True)
        if data is None:
            import json
            data = json.loads(request.data.decode('utf-8'))
        content = data.get('content')
        title = data.get('title', 'Untitled')
        knowledge_id = data.get('knowledge_id', 'dify-knowledge')

        if not content:
            return jsonify({'error': 'content is required'}), 400

        # Generate embedding
        vector = embedder.embed_text(content)

        # Upload to Pinecone
        import uuid
        pc_client.upsert(
            vectors=[vector],
            metadata=[{
                'content': content,
                'title': title,
                'knowledge_id': knowledge_id,
                'path': f'/documents/{knowledge_id}/{uuid.uuid4()}',
                'description': f'Document: {title}'
            }]
        )

        return jsonify({'status': 'success', 'message': 'Document uploaded'})
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
