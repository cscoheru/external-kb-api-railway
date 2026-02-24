import os

# API Keys (will be overridden by environment variables in Railway)
DIFY_API_KEY = os.getenv('DIFY_API_KEY', 'dify_external_kb_secret_key_2026')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_HOST = os.getenv('PINECONE_HOST')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'dify-knowledge')
QWEN_API_KEY = os.getenv('QWEN_API_KEY')
