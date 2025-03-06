import os
import shutil

from watgpt.constants import (
    EMBEDDINGS_MODEL_NAME,
    UNIVERSITY_DOCS_COLLECTION,
    VECTOR_DATABASE_FILE,
)
from watgpt.db.sql_db import SqlDB
from watgpt.db.vector_db import VectorDB
from watgpt.utils import create_marker_file, delete_marker_file, log_info


def clear_database():
    if os.path.exists(VECTOR_DATABASE_FILE):
        shutil.rmtree(VECTOR_DATABASE_FILE)


def main():
    delete_marker_file('create_vector_db.done')

    # 1) Initialize tables (optional if not yet done)
    sql_db = SqlDB()

    # 2) Fetch all chunks
    chunks_in_db = sql_db.fetch_all_chunks()
    log_info(f'All chunks in db => total {len(chunks_in_db)} rows.')

    # 3) Init vector database
    vector_db = VectorDB(
        db_file=VECTOR_DATABASE_FILE,
        collection_name=UNIVERSITY_DOCS_COLLECTION,
        embeddings_model_name=EMBEDDINGS_MODEL_NAME,
    )

    for chunk in chunks_in_db:
        vector_db.add_chunk(chunk)
    log_info('All chunks added to ChromaDB.')
    create_marker_file('create_vector_db.done')


if __name__ == '__main__':
    clear_database()
    main()
