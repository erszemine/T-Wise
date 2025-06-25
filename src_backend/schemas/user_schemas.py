from pydantic import BaseModel, Field, EmailStr
from beanie import PydanticObjectId # MongoDB ObjectID'leri için Pydantic uyumlu tip
from typing import Optional, List
from datetime import datetime

from ..enums import UserPosition # Burayı ekliyoruz!


# Kullanıcı oluşturmak için gelen istek gövdesinin şeması (POST /users/)
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Kullanıcı adı")
    password: str = Field(..., min_length=6, description="Kullanıcı şifresi") # Ham şifre buraya gelir
    email: Optional[EmailStr] = Field(None, description="Kullanıcının e-posta adresi")
    first_name: Optional[str] = Field(None, max_length=50, description="Kullanıcının adı")
    last_name: Optional[str] = Field(None, max_length=50, description="Kullanıcının soyadı")
    # position tipini UserPosition enum'ı olarak değiştiriyoruz ve varsayılan değer veriyoruz
    position: UserPosition = Field(UserPosition.STOK_KONTROL_UZMANI, description="Kullanıcının pozisyonu") # BURADA DEĞİŞİKLİK
    
    # password_hash client'tan gelmez, server'da oluşturulur, bu yüzden buradan kaldırıyoruz
    # password_hash: Optional[str] = None 
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "newuser",
                    "password": "SecurePassword123",
                    "email": "newuser@example.com",
                    "first_name": "Ayşe",
                    "last_name": "Yılmaz",
                    "position": UserPosition.STOK_KONTROL_UZMANI.value # Enum değerini string olarak örnekte gösteriyoruz
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
    # position tipini UserPosition enum'ı olarak değiştiriyoruz
    position: Optional[UserPosition] = Field(None, description="Güncellenmiş pozisyon") # BURADA DEĞİŞİKLİK
    is_active: Optional[bool] = Field(None, description="Kullanıcının aktiflik durumu")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "updated@example.com",
                    "is_active": False,
                    "position": UserPosition.DEPO_YONETICISI.value # Enum değerini string olarak örnekte gösteriyoruz
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
    # position tipini UserPosition enum'ı olarak değiştiriyoruz
    position: UserPosition = Field(description="Kullanıcının pozisyonu") # BURADA DEĞİŞİKLİK
    is_active: bool = Field(description="Kullanıcının aktiflik durumu")
    created_at: datetime = Field(description="Kullanıcının oluşturulma tarihi")
    updated_at: Optional[datetime] = Field(None, description="Kullanıcının son güncellenme tarihi")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True, # Beanie User Document'tan dönüşüm için
        "json_encoders": {
            PydanticObjectId: str,
            datetime: lambda v: v.isoformat() + "Z"
        },
        "arbitrary_types_allowed": True
    }

# Kullanıcının pozisyonunu güncellemek için özel şema (PATCH /users/{id}/position)
class UserPositionUpdate(BaseModel):
    # position tipini UserPosition enum'ı olarak değiştiriyoruz
    position: UserPosition = Field(..., description="Kullanıcının yeni pozisyonu") # BURADA DEĞİĞİŞİKLİK

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"position": UserPosition.KALITE_KONTROL_UZMANI.value} # Enum değerini string olarak örnekte gösteriyoruz
            ]
        }
    }