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