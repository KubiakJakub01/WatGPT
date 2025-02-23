from ..constants import (
    CHUNKS_DATABASE_FILE,
    EMBEDDINGS_MODEL_NAME,
    UNIVERSITY_DOCS_COLLECTION,
    VECTOR_DATABASE_FILE,
)
from ..db import ChunkDB, VectorDB
from ..utils import clear_database, log_info


def main():
    # Init chunk database
    chunk_db = ChunkDB(CHUNKS_DATABASE_FILE)
    chunks_in_db = chunk_db.fetch_all_chunks()
    log_info(f'All PDF chunks in db => total {len(chunks_in_db)} rows.')
    chunk_db.close()

    # Init vector database
    vector_db = VectorDB(VECTOR_DATABASE_FILE, UNIVERSITY_DOCS_COLLECTION, EMBEDDINGS_MODEL_NAME)

    # Add chunks to vector database
    for chunk in chunks_in_db:
        vector_db.add_chunk(chunk)
    log_info('All chunks added to ChromaDB.')


if __name__ == '__main__':
    clear_database(VECTOR_DATABASE_FILE)
    main()
