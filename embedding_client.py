import requests
import logging

logger = logging.getLogger(__name__)

class QwenEmbedding:
    def __init__(self, api_key: str, model: str = "text-embedding-v2"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"

    def embed_text(self, text: str) -> list:
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': self.model,
                'input': {'texts': [text]},
                'parameters': {
                    'text_type': 'document',
                    'embedding_type': 'float'
                }
            }
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Check for API error (Dashscope returns 'code' field on error)
            if 'code' in result and result['code'] != 'Success':
                raise Exception(f"Qwen API error: {result.get('message', 'Unknown error')}")

            embedding = result['output']['embeddings'][0]['embedding']
            return embedding
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise
