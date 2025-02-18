import argparse

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
    log_info(f"Top 3 relevant documents for query '{query}':")
    for i, result in enumerate(results, start=1):
        log_info(f'{i}. {result}')


if __name__ == '__main__':
    args = parse_args()
    main(args.query)
