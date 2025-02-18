import argparse
from pathlib import Path

from ..constants import EMBEDDINGS_MODEL_NAME, UNIVERSITY_DOCS_COLLECTION, VECTOR_DATABASE_FILE
from ..db import VectorDB
from ..utils import log_info


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--query',
        type=str,
        required=True,
        help='Query string to search in the database.',
    )
    return parser.parse_args()


def main(query):
    # Init vector database
    vector_db = VectorDB(VECTOR_DATABASE_FILE, UNIVERSITY_DOCS_COLLECTION, EMBEDDINGS_MODEL_NAME)

    # Query the database
    results = vector_db.query(query)
    for doc, score, metadata in zip(
        results['documents'][0], results['distances'][0], results['metadatas'][0], strict=False
    ):
        source = Path(metadata['source_file']).name
        log_info(f'Found: {doc} (Similarity Score: {score}) (Source: {source})')


if __name__ == '__main__':
    args = parse_args()
    main(args.query)
