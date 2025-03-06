from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from ..constants import (
    EMBEDDINGS_MODEL_NAME,
    UNIVERSITY_DOCS_COLLECTION,
    VECTOR_DATABASE_FILE,
)
from ..utils import log_info
from .models import Chunk


class VectorDB:
    def __init__(
        self,
        db_file: str = VECTOR_DATABASE_FILE,
        collection_name: str = UNIVERSITY_DOCS_COLLECTION,
        embeddings_model_name: str = EMBEDDINGS_MODEL_NAME,
    ):
        """
        Initialize ChromaDB using LangChain's Chroma wrapper.

        :param db_file: Path to the ChromaDB database.
        :param collection_name: Name of the collection in ChromaDB.
        :param embeddings_model_name: Hugging Face model for embedding generation.
        """
        self.embedding_function = HuggingFaceEmbeddings(model_name=embeddings_model_name)

        # Initialize LangChain's Chroma vector store
        self.vector_store = Chroma(
            collection_name=collection_name,
            persist_directory=db_file,
            embedding_function=self.embedding_function,
        )

    def add_chunk(self, chunk: Chunk):
        """
        Add a Chunk model instance to ChromaDB if it doesn't already exist.
        """
        # Check if the document is already in the vector store
        existing_docs = self.vector_store.get([str(chunk.chunk_id)])
        if existing_docs['ids']:
            log_info(f'Chunk {chunk.chunk_id} already exists in vector DB. Skipping.')
            return

        # Prepare metadata ensuring no None values exist (convert None to empty string)
        metadata = {
            'chunk_id': chunk.chunk_id,
            'source_url': chunk.source_url if chunk.source_url is not None else '',
            'file_url': chunk.file_url if chunk.file_url is not None else '',
            'title': chunk.title if chunk.title is not None else '',
            'date': str(chunk.date) if chunk.date is not None else '',
        }

        # Convert to LangChain Document format
        document = Document(
            page_content=chunk.content,
            metadata=metadata,
        )

        # Add the document to Chroma
        self.vector_store.add_documents([document])
        log_info(f'Chunk {chunk.chunk_id} added to ChromaDB.')

    def query(self, query: str, top_k: int = 3):
        """
        Retrieve top-k relevant chunks from ChromaDB using similarity search.

        :param query: User query string.
        :param top_k: Number of top matches to retrieve.
        :return: List of Document objects (LangChain).
        """
        results = self.vector_store.similarity_search(query, k=top_k)
        return results
