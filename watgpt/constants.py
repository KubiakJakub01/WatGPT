from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHUNKS_DATABASE_FILE: str = str(PROJECT_ROOT / 'chunks.db')
VECTOR_DATABASE_FILE: str = str(PROJECT_ROOT / 'vectors.db')
DATA_DIR_PATH = PROJECT_ROOT / 'wat_data'
CONFIG_DIR_PATH = PROJECT_ROOT / 'config'
TIMETABLE_URL = 'https://planzajec.wcy.wat.edu.pl/pl/rozklad?grupa_id={group}'
CALENDAR_PDF_FP = (
    DATA_DIR_PATH
    / 'zal._nr_1_organizacja_zajec_w_roku_akademickim_2024_2025_na_studiach_stacjonarnych.pdf'
)
STRUCTURED_PDF_FP = DATA_DIR_PATH / 'informator_dla_studentow_1_roku_2024.pdf'
EMBEDDINGS_MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
UNIVERSITY_DOCS_COLLECTION = 'university_docs'
PROMPTS_FILE = CONFIG_DIR_PATH / 'prompts.yaml'
LLM_RAG_SYSTEM_PROMPT = 'llm_rag_system_prompt'
