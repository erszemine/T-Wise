# src_backend/api/auth_routes.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

from ..models_entity.User import User
from ..security import create_access_token, authenticate_user, hash_password
from ..schemas.user_schemas import UserCreate, UserResponse
from ..enums import UserPosition
from ..security import role_required


router = APIRouter(prefix="/api", tags=["Authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/token", response_model=Token, summary="Kullanıcı girişi ve erişim token'ı al")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yanlış kullanıcı adı veya parola",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hesap aktif değil")

    access_token_data = {
        "sub": str(user.id),
        "username": user.username,
        "position": user.position.value
    }
    
    access_token = create_access_token(data=access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Yeni kullanıcı kaydı")
async def register_user(
    user_data: UserCreate,
    # Sadece Administrator yetkisine sahip kullanıcıların yeni kayıt yapmasına izin ver
    current_user: User = Depends(role_required([UserPosition.ADMIN])) 
):
    existing_user = await User.find_one(User.username == user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kullanıcı adı zaten mevcut")

    if user_data.email:
        existing_email_user = await User.find_one(User.email == user_data.email)
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-posta adresi zaten kullanımda")

    hashed_password = hash_password(user_data.password)

    user_dict = user_data.model_dump()
    user_dict.pop("password")
    user_dict["password_hash"] = hashed_password # hashed_password -> password_hash olarak DEĞİŞTİRİLDİ
    
    new_user = User(**user_dict)
    await new_user.insert()
    
    return {"username": new_user.username, "message": "Kullanıcı başarıyla kaydedildi."}