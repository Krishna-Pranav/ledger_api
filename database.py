from sqlalchemy import create_engine
from config import settings
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

engine = create_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()