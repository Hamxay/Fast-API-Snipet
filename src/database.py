from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.utils.config import DATABASE_URL

# as we are running our project from app folder as root
# we will use ./blog.db
SQLALCHAMY_DATABASE_URL = DATABASE_URL
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHAMY_DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

#  A base class for declarative models. It will be used as a base class for all the models in the project.
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Add this function to create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)
