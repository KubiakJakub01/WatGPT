import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from watgpt.db.models import Base

# Get an absolute path to your project root, e.g. up from 'db/database.py'
DB_PATH = (Path(__file__).parent.parent.parent / "chunks.db").resolve()
# e.g. /home/maciek/WatGPT/chunks.db

DATABASE_URL = f"sqlite:///{DB_PATH}"   # 3 slashes + str(DB_PATH)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print(f"Created tables in {DB_PATH}")
