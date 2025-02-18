from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

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

    def add_chunk(self, chunk: ChunkRow):
        """
        Add a document chunk to ChromaDB if it doesn't already exist.

        :param chunk: ChunkRow containing text and metadata.
        """
        # Check if chunk already exists
        existing_docs = self.vector_store.get([str(chunk.chunk_id)])
        if existing_docs['ids']:  # If IDs exist, chunk is already present
            log_info(f'Chunk {chunk.chunk_id} already exists. Skipping.')
            return

        # Convert to LangChain Document format
        document = Document(
            page_content=chunk.content,
            metadata={
                'chunk_id': chunk.chunk_id,
                'heading': chunk.heading,
                'source_file': chunk.source_file,
                'page_num': chunk.page_number,
            },
        )

        # Add document to Chroma
        self.vector_store.add_documents([document])
        log_info(f'Chunk {chunk.chunk_id} added to ChromaDB.')

    def query(self, query: str, top_k: int = 3):
        """
        Retrieve top-k relevant chunks from ChromaDB using similarity search.

        :param query: User query string.
        :param top_k: Number of top matches to retrieve.
        :return: List of relevant chunk texts.
        """
        results = self.vector_store.similarity_search(query, k=top_k)
        return results
