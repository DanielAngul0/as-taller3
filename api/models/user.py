from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from api.database import Base

class User(Base):
    __tablename__ = "users"
    
    
        id = Column(Integer, primary_key=True, autoincrement=True)
        username = Column(String(50), unique=True, nullable=False)
        email = Column(String(120), unique=True, nullable=False)
        password_hash = Column(String(128), nullable=False)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        # TODO: Implementar representación del objeto
        pass