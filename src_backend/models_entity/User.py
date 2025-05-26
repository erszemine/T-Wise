from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "Users" # Veritabanındaki tablo adı

    id = Column(Integer, primary_key=True, index=True) # calisanID -> id
    position = Column(String(50), nullable=False) 
    password_hash = Column(String(255), nullable=False) # sifre -> password_hash (güvenlik için hash'li saklarız)
    first_name = Column(String(100), nullable=True) 
    last_name = Column(String(100), nullable=True) 
    email = Column(String(100), unique=True, index=True, nullable=True) 
    phone = Column(String(20), nullable=True) 
    username = Column(String(50), unique=True, index=True, nullable=False) 
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now()) 

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', position='{self.position}')>"