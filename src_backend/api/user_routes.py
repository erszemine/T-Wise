from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from beanie import PydanticObjectId # bson.objectid.ObjectId yerine PydanticObjectId
from datetime import datetime

# models_entity'den User modelini import ediyoruz
from ..models_entity.User import User 

# Güvenlik modüllerini import ediyoruz
from ..security import role_required, get_current_user, hash_password

# Schema'ları import ediyoruz
from ..schemas.user_schemas import UserCreate, UserUpdate, UserResponse, UserPositionUpdate

# Enums'ı import ediyoruz!
from ..enums import UserPosition 

router = APIRouter(prefix="/api/users", tags=["Users"]) # Router'a prefix ve tags eklemek iyi bir pratiktir

# Kullanıcı oluşturma endpoint'i 
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Yeni kullanıcı oluştur (Yönetici yetkisi)")
async def create_user(user_data: UserCreate, current_user: User = Depends(role_required([UserPosition.ADMIN]))): # BURADA DEĞİŞİKLİK
    # Kullanıcı adı zaten var mı kontrol et
    existing_user = await User.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Kullanıcı adı zaten kullanımda.")
    
    # E-posta zaten var mı kontrol et (isteğe bağlı, ama iyi bir pratiktir)
    if user_data.email:
        existing_email_user = await User.find_one({"email": user_data.email})
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-posta adresi zaten kullanımda.")

    # Şifreyi hash'lemeden önce UserCreate modelinden password'i al
    user_dict = user_data.model_dump() # Pydantic v2 için model_dump()
    password = user_dict.pop("password") # Ham şifreyi al ve kaldır
    user_dict["password_hash"] = hash_password(password) # password_hash -> hashed_password olarak DEĞİŞTİRİLDİ

    # 'role' yerine 'position' kullanın (user_schemas'ı da bu şekilde güncelleyeceğiz)
    # user_data'dan gelen pozisyon doğru tipte (UserPosition) olacağı için bu if bloğu gereksizleşir
    # if 'role' in user_dict:
    #     user_dict['position'] = user_dict.pop('role')

    # Eksik alanlar için varsayılan değerler zaten UserCreate modelinde tanımlı olmalı,
    # ancak burada bir güvenlik katmanı olarak da bırakılabilir.
    if 'first_name' not in user_dict or user_dict['first_name'] is None:
        user_dict['first_name'] = ""
    if 'last_name' not in user_dict or user_dict['last_name'] is None:
        user_dict['last_name'] = ""
    
    # User modeline uygun hale getir
    new_user = User(**user_dict)
    
    await new_user.insert()
    return UserResponse.model_validate(new_user) # parse_obj(new_user.dict()) -> model_validate(new_user) olarak DEĞİŞTİRİLDİ

@router.get("/", response_model=List[UserResponse], summary="Tüm kullanıcıları listele (Yönetici yetkisi)")
async def get_all_users(current_user: User = Depends(role_required([UserPosition.ADMIN]))): # BURADA DEĞİŞİKLİK
    users = await User.find_all().to_list()
    return [UserResponse.model_validate(u) for u in users] # parse_obj(u.dict()) -> model_validate(u) olarak DEĞİŞTİRİLDİ

@router.get("/me", response_model=UserResponse, summary="Oturumdaki kullanıcı bilgilerini getir")
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user) # parse_obj(current_user.dict()) -> model_validate(current_user) olarak DEĞİŞTİRİLDİ

@router.put("/{user_id}", response_model=UserResponse, summary="Bir kullanıcıyı ID ile güncelle (Yönetici yetkisi)")
async def update_user(user_id: str, user_update: UserUpdate, current_user: User = Depends(role_required([UserPosition.ADMIN]))): # BURADA DEĞİŞİKLİK
    try:
        user = await User.get(PydanticObjectId(user_id)) # ObjectId -> PydanticObjectId olarak DEĞİŞTİRİLDİ
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        update_data = user_update.model_dump(exclude_unset=True) # Pydantic v2 için model_dump()
        
        # 'role' yerine 'position' düzeltmesi: user_schemas'ta 'position' zaten doğru tipte olacağı için
        # bu kontrol genellikle gereksizleşir. Direkt update_data['position'] erişimi yeterli olur.
        # if 'role' in update_data: 
        #     update_data['position'] = update_data.pop('role')

        if 'password' in update_data and update_data['password']:
            update_data['password_hash'] = hash_password(update_data['password']) # password_hash -> hashed_password olarak DEĞİŞTİRİLDİ
            del update_data['password']

        for key, value in update_data.items():
            setattr(user, key, value)

        user.updated_at = datetime.now()
        await user.save()
        return UserResponse.model_validate(user) # parse_obj(user.dict()) -> model_validate(user) olarak DEĞİŞTİRİLDİ
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Güncelleme hatası: {e}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Bir kullanıcıyı ID ile sil (Yönetici yetkisi)")
async def delete_user(user_id: str, current_user: User = Depends(role_required([UserPosition.ADMIN]))): # BURADA DEĞİŞİKLİK
    try:
        user = await User.get(PydanticObjectId(user_id)) # ObjectId -> PydanticObjectId olarak DEĞİŞTİRİLDİ
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

# Eğer kullanıcı pozisyonunu ayrı bir endpoint ile güncellemek isterseniz (Opsiyonel)
@router.patch("/{user_id}/position", response_model=UserResponse, summary="Kullanıcı pozisyonunu güncelle (Yönetici yetkisi)")
async def update_user_position(user_id: str, position_update: UserPositionUpdate, current_user: User = Depends(role_required([UserPosition.ADMIN]))): # BURADA DEĞİŞİKLİK
    try:
        user = await User.get(PydanticObjectId(user_id)) # ObjectId -> PydanticObjectId olarak DEĞİŞTİRİLDİ
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı")

        user.position = position_update.position # 'role' yerine 'position' alanı kullanılıyor
        user.updated_at = datetime.now()
        await user.save()
        return UserResponse.model_validate(user) # parse_obj(user.dict()) -> model_validate(user) olarak DEĞİŞTİRİLDİ
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pozisyon güncelleme hatası: {e}") # Hata mesajı da güncellendi