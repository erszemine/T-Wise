# src_backend/api/user_routes.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field

from models_entity.User import User
from security import role_required, get_current_user, hash_password

router = APIRouter()

class UserResponse(User):
    id: str = Field(alias="_id")
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    position: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None # Kullanıcı aktiflik durumunu güncellemek için

@router.get("/", response_model=List[UserResponse], summary="Tüm kullanıcıları listele (Yönetici yetkisi)")
async def get_all_users(current_user: User = Depends(role_required(["Yönetici"]))):
    users = await User.find_all().to_list()
    return [UserResponse.parse_obj(u.dict()) for u in users]

@router.get("/me", response_model=UserResponse, summary="Oturumdaki kullanıcı bilgilerini getir")
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.parse_obj(current_user.dict())

@router.put("/{user_id}", response_model=UserResponse, summary="Bir kullanıcıyı ID ile güncelle (Yönetici yetkisi)")
async def update_user(user_id: str, user_update: UserUpdate, current_user: User = Depends(role_required(["Yönetici"]))):
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        update_data = user_update.dict(exclude_unset=True)
        if 'password' in update_data and update_data['password']:
            update_data['password_hash'] = hash_password(update_data['password'])
            del update_data['password']

        for key, value in update_data.items():
            setattr(user, key, value)

        user.updated_at = datetime.now()
        await user.save()
        return UserResponse.parse_obj(user.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Güncelleme hatası: {e}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Bir kullanıcıyı ID ile sil (Yönetici yetkisi)")
async def delete_user(user_id: str, current_user: User = Depends(role_required(["Yönetici"]))):
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        # Kendini silmeyi engelle
        if user.id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kendi hesabınızı silemezsiniz.")

        await user.delete()
        return
    except HTTPException as e: # Kendi attığımız HTTP hatalarını yakala
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Silme hatası: {e}")