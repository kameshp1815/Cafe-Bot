from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from urllib.parse import quote_plus
from settings import settings

password = quote_plus(settings.db_password)

DATABASE_URL = (
    f"postgresql+psycopg2://{settings.db_username}:{password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}?sslmode=require"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()