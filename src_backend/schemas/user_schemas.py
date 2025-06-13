# src/stok_yonetim_backend/schemas/user_schemas.py
from pydantic import BaseModel, Field, EmailStr
from beanie import PydanticObjectId # MongoDB ObjectID'leri için Pydantic uyumlu tip
from typing import Optional, List
from datetime import datetime

# Kullanıcı oluşturmak için gelen istek gövdesinin şeması (POST /users/)
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Kullanıcı adı")
    password: str = Field(..., min_length=6, description="Kullanıcı şifresi") # Ham şifre buraya gelir
    email: Optional[EmailStr] = Field(None, description="Kullanıcının e-posta adresi")
    first_name: Optional[str] = Field(None, max_length=50, description="Kullanıcının adı")
    last_name: Optional[str] = Field(None, max_length=50, description="Kullanıcının soyadı")
    position: Optional[str] = Field("user", description="Kullanıcının rolü (örn: admin, manager, user)") # Varsayılan rol

    # password_hash alanı, API'ye gelen isteklerde beklenmez,
    # backend tarafında şifre hash'lendikten sonra atanır.
    # Bu yüzden Pydantic modelinde var ama isteğe bağlı ve varsayılanı yok.
    password_hash: Optional[str] = None 

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "newuser",
                    "password": "SecurePassword123",
                    "email": "newuser@example.com",
                    "first_name": "Ayşe",
                    "last_name": "Yılmaz",
                    "role": "user"
                }
            ]
        }
    }

# Kullanıcı güncellemek için gelen istek gövdesinin şeması (PUT /users/{id} veya PATCH /users/{id})
# Tüm alanlar Optional olmalı.
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Güncellenmiş kullanıcı adı")
    password: Optional[str] = Field(None, min_length=6, description="Yeni şifre (isteğe bağlı)")
    email: Optional[EmailStr] = Field(None, description="Güncellenmiş e-posta adresi")
    first_name: Optional[str] = Field(None, max_length=50, description="Güncellenmiş adı")
    last_name: Optional[str] = Field(None, max_length=50, description="Güncellenmiş soyadı")
    role: Optional[str] = Field(None, description="Güncellenmiş rol")
    is_active: Optional[bool] = Field(None, description="Kullanıcının aktiflik durumu")

    # password_hash alanı, API'ye gelen isteklerde beklenmez.
    password_hash: Optional[str] = None 

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "updated@example.com",
                    "is_active": False
                }
            ]
        }
    }

# API'den kullanıcı bilgilerini dönerken kullanılan şema (GET, POST, PUT yanıtları)
# Şifre hash'i gibi hassas bilgiler döndürülmez.
class UserResponse(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id", description="Kullanıcının MongoDB ID'si")
    username: str = Field(description="Kullanıcı adı")
    email: Optional[EmailStr] = Field(None, description="Kullanıcının e-posta adresi")
    first_name: Optional[str] = Field(None, description="Kullanıcının adı")
    last_name: Optional[str] = Field(None, description="Kullanıcının soyadı")
    role: str = Field(description="Kullanıcının rolü")
    is_active: bool = Field(description="Kullanıcının aktiflik durumu")
    created_at: datetime = Field(description="Kullanıcının oluşturulma tarihi")
    updated_at: datetime = Field(description="Kullanıcının son güncellenme tarihi")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "60c72b2f9f1b2c3d4e5f6a7c",
                    "username": "adminuser",
                    "email": "admin@example.com",
                    "first_name": "Can",
                    "last_name": "Demir",
                    "role": "admin",
                    "is_active": True,
                    "created_at": "2023-01-01T10:00:00.000Z",
                    "updated_at": "2023-01-01T10:00:00.000Z"
                }
            ]
        }
    }

# Kullanıcının rolünü güncellemek için özel şema (PATCH /users/{id}/role)
class UserRoleUpdate(BaseModel):
    role: str = Field(..., description="Kullanıcının yeni rolü (örn: admin, manager, user)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"role": "manager"}
            ]
        }
    }