import logging
from datetime import datetime
from pathlib import Path

import coloredlogs
import dateparser
import yaml

from .constants import LLM_RAG_SYSTEM_PROMPT, PROMPTS_FILE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('debug.log', mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
file_handler.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(coloredlogs.ColoredFormatter('%(asctime)s %(levelname)s %(message)s'))
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(file_handler)


def log_debug(*args, **kwargs):
    """Log an debug message."""
    logger.debug(*args, **kwargs)


def log_info(*args, **kwargs):
    """Log an info message."""
    logger.info(*args, **kwargs)


def log_warning(*args, **kwargs):
    """Log a warning message."""
    logger.warning(*args, **kwargs)


def log_error(*args, **kwargs):
    """Log an error message."""
    logger.error(*args, **kwargs)


def load_prompt(filepath: Path = PROMPTS_FILE, prompt_name: str = LLM_RAG_SYSTEM_PROMPT) -> str:
    """Load a prompt from a YAML file."""
    with open(filepath, encoding='utf-8') as file:
        prompts = yaml.safe_load(file)
    return prompts[prompt_name]


def convert_natural_date_to_iso(raw_date: str) -> str | None:
    """
    Convert a natural language date
    (e.g., "jutro", "w przyszły poniedziałek") to ISO 8601 format (YYYY-MM-DD).

    :param raw_date: Raw text representation of the date.
    :return: Converted date in ISO format, or None if parsing fails.
    """
    if not raw_date:
        return None

    today = datetime.today()
    parsed_date = dateparser.parse(raw_date, settings={'RELATIVE_BASE': today})

    return parsed_date.strftime('%Y_%m_%d') if parsed_date else None
