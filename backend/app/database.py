import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
# Vercel serverless functions have a read-only project filesystem. /tmp is writable
# but ephemeral, so database state should be treated as DEMO/SESSION data there.
if os.getenv("VERCEL"):
    DB_DIR = Path("/tmp") / "sahakar-sahayak"
else:
    DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{(DB_DIR / 'sahakar_sahayak.db').as_posix()}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
