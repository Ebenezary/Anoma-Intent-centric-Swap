from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Intent(Base):
    __tablename__ = "intents"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String, index=True)
    offer = Column(String, index=True)
    want = Column(String, index=True)
    deadline = Column(String, nullable=True)
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    chain = Column(String)  # comma-separated list of intent IDs for simplicity
    created_at = Column(DateTime, default=datetime.utcnow)
