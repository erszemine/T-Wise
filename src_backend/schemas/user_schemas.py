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
    position: Optional[str] = Field("user", description="Kullanıcının pozisyonu (örn: Yönetici, Çalışan, Depo Sorumlusu)") # role yerine position

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
                    "position": "user" # role yerine position
                }
            ]
        }
    }

# Kullanıcı güncellemek için gelen istek gövdesinin şeması (PUT /users/{id} veya PATCH /users/{id})
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Güncellenmiş kullanıcı adı")
    password: Optional[str] = Field(None, min_length=6, description="Yeni şifre (isteğe bağlı)")
    email: Optional[EmailStr] = Field(None, description="Güncellenmiş e-posta adresi")
    first_name: Optional[str] = Field(None, max_length=50, description="Güncellenmiş adı")
    last_name: Optional[str] = Field(None, max_length=50, description="Güncellenmiş soyadı")
    position: Optional[str] = Field(None, description="Güncellenmiş pozisyon") # role yerine position
    is_active: Optional[bool] = Field(None, description="Kullanıcının aktiflik durumu")

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
class UserResponse(BaseModel):
    id: PydanticObjectId = Field(..., alias="_id", description="Kullanıcının MongoDB ID'si")
    username: str = Field(description="Kullanıcı adı")
    email: Optional[EmailStr] = Field(None, description="Kullanıcının e-posta adresi")
    first_name: Optional[str] = Field(None, description="Kullanıcının adı")
    last_name: Optional[str] = Field(None, description="Kullanıcının soyadı")
    position: str = Field(description="Kullanıcının pozisyonu") # role yerine position
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
                    "position": "Yönetici", # role yerine position
                    "is_active": True,
                    "created_at": "2023-01-01T10:00:00.000Z",
                    "updated_at": "2023-01-01T10:00:00.000Z"
                }
            ]
        }
    }

# Kullanıcının pozisyonunu güncellemek için özel şema (PATCH /users/{id}/position)
class UserPositionUpdate(BaseModel): # UserRoleUpdate yerine UserPositionUpdate yaptım
    position: str = Field(..., description="Kullanıcının yeni pozisyonu (örn: Yönetici, Çalışan, Depo Sorumlusu)") # role yerine position

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"position": "Çalışan"} # role yerine position
            ]
        }
    }