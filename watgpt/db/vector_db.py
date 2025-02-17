import chromadb
from sentence_transformers import SentenceTransformer

from ..constants import EMBEDDINGS_MODEL_NAME, UNIVERSITY_DOCS_COLLECTION, VECTOR_DATABASE_FILE
from ..utils import log_info
from .models import ChunkRow


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

    def add_chunk(self, chunk: ChunkRow):
        existing_chunk = self.collection.get(ids=[str(chunk.chunk_id)])

        if existing_chunk and existing_chunk['ids']:
            log_info(f'Chunk {chunk.chunk_id} already exists in the collection. Skipping.')
            return

        embeddings = self.model.encode(chunk.content).tolist()
        self.collection.add(
            ids=[str(chunk.chunk_id)],
            embeddings=[embeddings],
            metadatas=[
                {
                    'heading': chunk.heading,
                    'source_file': chunk.source_file,
                    'page_num': chunk.page_number,
                }
            ],
            documents=[chunk.content],
        )
        log_info(f'Chunk {chunk.chunk_id} added to the collection.')

    def query(self, query):
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(query_embeddings=query_embedding, n_results=3)
        return results
