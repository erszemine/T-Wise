# backend/src/stok_yonetim_backend/models/user.py (Güncellenmiş hali)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base

# Kullanıcılar ve Roller arasındaki çoktan çoğa ilişki için ilişki tablosu
# Bu, 'users' tablosundaki 'id' ile 'roles' tablosundaki 'id'yi bağlar
user_roles_association = Table(
    "user_roles_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    position = Column(String(50), nullable=False) # Bu, pozisyonu string olarak tutabilir, daha sonra Role ile eşlenebilir
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    stock_movements = relationship("StockMovement", back_populates="user")

    # Kullanıcının sahip olduğu rollere erişim için ilişki
    # secondary: İlişki tablosunu belirtir.
    # back_populates: Role modelindeki 'users' ilişkisiyle eşleşir.
    roles = relationship("Role", secondary=user_roles_association, back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', position='{self.position}')>"