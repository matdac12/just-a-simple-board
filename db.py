import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Create .kanban directory in the parent project (one level up from kanbanlite)
KANBAN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".kanban")
os.makedirs(KANBAN_DIR, exist_ok=True)

# Database path in the .kanban directory
DB_PATH = os.environ.get("KANBAN_DB_PATH", os.path.join(KANBAN_DIR, "app.db"))
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
