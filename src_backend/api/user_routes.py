from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime

# models_entity'den User modelini import ediyoruz
from models_entity.User import User 

# Güvenlik modüllerini import ediyoruz
from security import role_required, get_current_user, hash_password

# Schema'ları import ediyoruz (Yeni: 'schemas/user_schemas.py' dosyasından)
from schemas.user_schemas import UserCreate, UserUpdate, UserResponse, UserPositionUpdate

router = APIRouter()

# Kullanıcı oluşturma endpoint'i 
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Yeni kullanıcı oluştur (Yönetici yetkisi)")
async def create_user(user_data: UserCreate, current_user: User = Depends(role_required(["Yönetici"]))):
    # Kullanıcı adı zaten var mı kontrol et
    existing_user = await User.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Kullanıcı adı zaten kullanımda.")
    
    # E-posta zaten var mı kontrol et (isteğe bağlı, ama iyi bir pratiktir)
    if user_data.email:
        existing_email_user = await User.find_one({"email": user_data.email})
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-posta adresi zaten kullanımda.")

    # Şifreyi hash'lemeden önce UserCreate modelinden password_hash'i temizle
    # user_data.dict() yerine Pydantic'in model_dump() veya model_dump_json() metodlarını kullanın
    user_dict = user_data.model_dump()
    password = user_dict.pop("password") # Ham şifreyi al ve kaldır
    user_dict["password_hash"] = hash_password(password) # Hashlenmiş şifreyi ekle

    # 'role' yerine 'position' kullanın (önemli düzeltme)
    if 'role' in user_dict: # user_schemas'ta 'role' varsa
        user_dict['position'] = user_dict.pop('role') # 'role'u 'position'a dönüştür

    # Eksik alanlar için varsayılan değerleri veya kontrolleri yapabilirsiniz
    if 'first_name' not in user_dict or user_dict['first_name'] is None:
        user_dict['first_name'] = "" # Varsayılan boş string
    if 'last_name' not in user_dict or user_dict['last_name'] is None:
        user_dict['last_name'] = "" # Varsayılan boş string
    
    # User modeline uygun hale getir
    new_user = User(**user_dict)
    
    await new_user.insert()
    return UserResponse.parse_obj(new_user.dict())

@router.get("/", response_model=List[UserResponse], summary="Tüm kullanıcıları listele (Yönetici yetkisi)")
async def get_all_users(current_user: User = Depends(role_required(["Yönetici"]))):
    users = await User.find_all().to_list()
    # Pydantic v2'de parse_obj() yerine .model_validate() veya doğrudan model adını kullanmak daha iyidir.
    # Ancak burada Beanie'den dönen bir objeyi parse ediyoruz.
    return [UserResponse.parse_obj(u.dict()) for u in users] # Düzeltme: UserResponse.model_validate(u) de kullanabiliriz v2 için

@router.get("/me", response_model=UserResponse, summary="Oturumdaki kullanıcı bilgilerini getir")
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.parse_obj(current_user.dict()) # Düzeltme: UserResponse.model_validate(current_user)

@router.put("/{user_id}", response_model=UserResponse, summary="Bir kullanıcıyı ID ile güncelle (Yönetici yetkisi)")
async def update_user(user_id: str, user_update: UserUpdate, current_user: User = Depends(role_required(["Yönetici"]))):
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        update_data = user_update.model_dump(exclude_unset=True) # Pydantic v2 için model_dump()
        
        # 'role' yerine 'position' düzeltmesi
        if 'role' in update_data: # user_schemas'ta 'role' varsa
            update_data['position'] = update_data.pop('role') # 'role'u 'position'a dönüştür

        if 'password' in update_data and update_data['password']:
            update_data['password_hash'] = hash_password(update_data['password'])
            del update_data['password']

        for key, value in update_data.items():
            setattr(user, key, value)

        user.updated_at = datetime.now()
        await user.save()
        return UserResponse.parse_obj(user.dict()) # Düzeltme: UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Güncelleme hatası: {e}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Bir kullanıcıyı ID ile sil (Yönetici yetkisi)")
async def delete_user(user_id: str, current_user: User = Depends(role_required(["Yönetici"]))):
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        # Kendini silmeyi engelle
        if str(user.id) == str(current_user.id): # ObjectId karşılaştırması için str'ye çevir
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kendi hesabınızı silemezsiniz.")

        await user.delete()
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Silme hatası: {e}")

# Eğer kullanıcı rolünü ayrı bir endpoint ile güncellemek isterseniz (Opsiyonel)
@router.patch("/{user_id}/position", response_model=UserResponse, summary="Kullanıcı pozisyonunu güncelle (Yönetici yetkisi)")
async def update_user_position(user_id: str, position_update: UserPositionUpdate, current_user: User = Depends(role_required(["Yönetici"]))): # Parametre ve fonksiyon adı değişti
    try:
        user = await User.get(ObjectId(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        user.position = position_update.position # 'role' yerine 'position' alanı kullanılıyor
        user.updated_at = datetime.now()
        await user.save()
        return UserResponse.parse_obj(user.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pozisyon güncelleme hatası: {e}") # Hata mesajı da güncellendi