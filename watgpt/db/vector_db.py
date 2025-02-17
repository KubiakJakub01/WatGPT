import chromadb
from sentence_transformers import SentenceTransformer

from ..constants import EMBEDDINGS_MODEL_NAME, UNIVERSITY_DOCS_COLLECTION, VECTOR_DATABASE_FILE


class VectorDB:
    def __init__(
        self,
        db_file: str = VECTOR_DATABASE_FILE,
        collection_name: str = UNIVERSITY_DOCS_COLLECTION,
        embeddings_model_name: str = EMBEDDINGS_MODEL_NAME,
    ):
        self.client = chromadb.PersistentClient(path=db_file)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.model = SentenceTransformer(embeddings_model_name)

    def add_chunk(self, chunk_id, heading, content, source_file, page_num):
        embeddings = self.model.encode(content).tolist()
        self.collection.add(
            ids=[str(chunk_id)],
            embeddings=[embeddings],
            metadatas=[{'heading': heading, 'source_file': source_file, 'page_num': page_num}],
            documents=[content],
        )

    def query(self, query):
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(query_embeddings=query_embedding, n_results=3)
        return results
