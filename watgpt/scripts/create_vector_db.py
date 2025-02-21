# watgpt/scripts/create_vector_db.py
import os
import shutil
from watgpt.constants import (
    EMBEDDINGS_MODEL_NAME,
    UNIVERSITY_DOCS_COLLECTION,
    VECTOR_DATABASE_FILE,
)
from watgpt.utils import log_info
import watgpt.db.chunk_db as chunk_db
from watgpt.db.vector_db import VectorDB
from watgpt.db.database import init_db

def clear_database():
    if os.path.exists(VECTOR_DATABASE_FILE):
        shutil.rmtree(VECTOR_DATABASE_FILE)

def main():
    # 1) Initialize tables (optional if not yet done)
    init_db()

    # 2) Fetch all chunks
    chunks_in_db = chunk_db.fetch_all_chunks() 
    log_info(f'All chunks in db => total {len(chunks_in_db)} rows.')

    # 3) Init vector database
    vector_db = VectorDB(
        db_path=VECTOR_DATABASE_FILE,
        collection_name=UNIVERSITY_DOCS_COLLECTION,
        embeddings_model=EMBEDDINGS_MODEL_NAME
    )

    for chunk in chunks_in_db:
        vector_db.add_chunk(chunk)
    log_info('All chunks added to ChromaDB.')

if __name__ == '__main__':
    clear_database()
    main()
