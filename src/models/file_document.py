from sqlalchemy import Column, Integer, String
from src.database import Base


class FileDocument(Base):
    __tablename__ = "file_documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    storage_path = Column(String)
