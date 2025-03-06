from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_DIR = PROJECT_ROOT / 'databases'
CHUNKS_DATABASE_FILE: str = str(DATABASE_DIR / 'chunks.db')
VECTOR_DATABASE_FILE: str = str(DATABASE_DIR / 'vectors.db')
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
LLM_QUERY_EXTRACTION_PROMPT = 'llm_query_extraction_prompt'
LLM_PROVIDER = 'groq'
LLM_MODEL_NAME = 'llama3-8b-8192'
# ---- Values for Scrapy
ALLOWED_DOMAINS = ['wcy.wat.edu.pl']
START_URLS = ['https://www.wcy.wat.edu.pl/wydzial/ksztalcenie/informacje-studenci']
ALLOWED_PATHS = (str(Path('wydzial') / 'ksztalcenie' / 'informacje-studenci' / 'informator-1-rok'),)
DENIED_PATHS = (str(Path('karty-informacyjne-przedmiotow')), str(Path('kursy-mon')))
DENIED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
TARGET_GROUPS = 'WCY24IV1N2'
DEFAULT_BLOCK_HOURS = [
    ('block1', '08:00', '09:35'),
    ('block2', '09:50', '11:25'),
    ('block3', '11:40', '13:15'),
    ('block4', '13:30', '15:05'),
    ('block5', '15:45', '17:35'),
    ('block6', '17:50', '19:25'),
    ('block7', '19:40', '21:15'),
]
ALLOWED_EXTENSIONS = {
    'pdf',
    'doc',
    'docx',
    'odt',
    'rtf',
    'txt',
    'xls',
    'xlsx',
    'ods',
    'csv',
    'ppt',
    'pptx',
    'odp',
    'zip',
    'rar',
    '7z',
    'tar',
    'gz',
}
