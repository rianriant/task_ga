from sqlalchemy import Column, Integer, String, TIMESTAMP

from .database import Base


class FileRecord(Base):
    __tablename__ = "inbox"

    filename = Column(String, primary_key=True, index=True)
    bucket = Column(String)
    code = Column(Integer)
    registration_datetime = Column(TIMESTAMP)
