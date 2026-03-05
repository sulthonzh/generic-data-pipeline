from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=settings.pool_pre_ping,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from models.customer import Customer
    Base.metadata.create_all(bind=engine)


def get_engine():
    return engine
