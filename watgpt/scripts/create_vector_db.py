import os
import shutil

from ..constants import (
    CHUNKS_DATABASE_FILE,
    EMBEDDINGS_MODEL_NAME,
    UNIVERSITY_DOCS_COLLECTION,
    VECTOR_DATABASE_FILE,
)
from ..db import ChunkDB, VectorDB
from ..utils import log_info


def clear_database():
    if os.path.exists(VECTOR_DATABASE_FILE):
        shutil.rmtree(VECTOR_DATABASE_FILE)


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
        chunk_id = chunk['chunk_id']
        heading = chunk['heading']
        content = chunk['content']
        source_file = chunk['source_file']
        page_num = chunk['page_number']
        vector_db.add_chunk(chunk_id, heading, content, source_file, page_num)
        log_info(f'Added chunk_id={chunk_id} to ChromaDB.')
    log_info('All chunks added to ChromaDB.')


if __name__ == '__main__':
    clear_database()
    main()
