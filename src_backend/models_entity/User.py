'''
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class User(Document):
    username: str = Field(unique=True, index=True)
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = Field(unique=True, index=True) # E-posta da benzersiz olabilir
    position: str = "Employee" # Varsayılan pozisyon
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users" # MongoDB koleksiyon adı
        '''

# src_backend/models_entity/User.py
from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class User(Document):
    username: str = Field(unique=True, index=True, description="Kullanıcı adı (benzersiz)")
    password_hash: str = Field(description="Şifrenin hash değeri")
    first_name: str = Field(description="Kullanıcının adı")
    last_name: str = Field(description="Kullanıcının soyadı") 
    email: Optional[str] = Field(None, description="Kullanıcının e-posta adresi")
    position: str = Field(description="Kullanıcının rolü (ör: Yönetici, Depo Sorumlusu, Üretim Yöneticisi)") # Compass'taki position yerine role
    is_active: bool = Field(True, description="Kullanıcı aktif mi?") # Compass'tan geldi

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"