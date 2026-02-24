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
