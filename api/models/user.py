from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    # Define la tabla de usuarios
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # relación inversa con Cart:
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    
    # Representa el objeto User como una cadena
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', is_active"