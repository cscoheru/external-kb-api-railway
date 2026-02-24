from pinecone import Pinecone
import logging
import os

logger = logging.getLogger(__name__)

class PineconeClient:
    def __init__(self, api_key: str, host: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(host=host)
        self.index_name = index_name

    def query(self, vector: list, top_k: int = 3, filter: dict = None):
        try:
            result = self.index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            return result
        except Exception as e:
            logger.error(f"Pinecone query error: {str(e)}")
            raise

    def upsert(self, vectors: list, metadata: list):
        """Upsert vectors with metadata to Pinecone"""
        try:
            import uuid
            records = []
            for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                records.append({
                    'id': str(uuid.uuid4()),
                    'values': vector,
                    'metadata': meta
                })

            self.index.upsert(vectors=records)
            logger.info(f"Upserted {len(records)} vectors to Pinecone")
            return {'upserted_count': len(records)}
        except Exception as e:
            logger.error(f"Pinecone upsert error: {str(e)}")
            raise
