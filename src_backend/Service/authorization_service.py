# backend/src/stok_yonetim_backend/security.py (veya dependencies.py)
# Bu dosya aynı zamanda JWT doğrulama ve kullanıcı objesini alma işlemlerini de içerebilir.

from typing import List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models_entity import User
from enums import Permission 

# Dummy implementation for get_current_active_user
from fastapi import Depends

async def get_current_active_user(current_user: User = Depends(lambda: User(id=1, is_active=True))):
    # Replace this with your actual logic to get the current active user
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Devre dışı bırakılmış kullanıcı")
    return current_user

# Varsayımsal bir kullanıcı yetki veritabanı veya rol tablosu
# Gerçek uygulamada bu bilgiler veritabanından çekilmelidir.
# User modelinize 'roles' veya 'permissions' alanı eklenebilir.
# Veya ayrı bir 'UserPermission' tablosu (Adım 4'te bahsedilen) kullanılabilir.

# Örnek: Kullanıcının izinlerini veritabanından çekecek bir fonksiyon
async def get_user_permissions(user_id: int, db: AsyncSession) -> List[Permission]:
    # BURASI ÇOK ÖNEMLİ: Gerçekte bu fonksiyon,
    # user_id'ye sahip kullanıcının veritabanındaki izinlerini sorgulayacaktır.
    # Basit bir örnek için şimdilik manuel izinler tanımlayalım:

    # Kullanıcı 1: Depo Yöneticisi olsun
    if user_id == 1:
        return [
            Permission.DEPO_DUZENI_YONET,
            Permission.URUN_KABUL_ET,
            Permission.STOK_SEVIYESI_GUNCELLE,
            Permission.RAPOR_OLUSTUR
        ]
    # Kullanıcı 2: Stok Kontrol Uzmanı olsun
    elif user_id == 2:
        return [
            Permission.STOK_SEVIYESI_GUNCELLE,
            Permission.PARCA_DURUMU_KONTROL_ET,
            Permission.RAPOR_OLUSTUR
        ]
    # Kullanıcı 3: Tedarik Planlama Uzmanı olsun
    elif user_id == 3:
        return [
            Permission.EKSİK_PARCA_TEDARİK_ET,
            Permission.RAPOR_OLUSTUR
        ]
    # Diğer kullanıcılar:
    return []

# Yetkilendirme fonksiyonu (FastAPI Dependency olarak kullanılacak)
class Authorize:
    def __init__(self, required_permissions: List[Permission]):
        self.required_permissions = required_permissions

    async def __call__(self, 
                       current_user: User = Depends(get_current_active_user), # current_user'ı JWT ile almalıyız
                       db: AsyncSession = Depends(get_db)):

        user_permissions = await get_user_permissions(current_user.id, db)

        # Kullanıcının gerekli tüm yetkilere sahip olup olmadığını kontrol et
        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Erişim Reddedildi: '{permission.value}' yetkisi gerekli."
                )
        return True # Yetkilendirme başarılı

# get_current_active_user fonksiyonu (JWT doğrulamasını yapar ve kullanıcı objesini döndürür)
# Bu fonksiyon security.py içinde zaten olması gereken bir JWT doğrulama fonksiyonudur.
# Örnek:
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from .config import SECRET_KEY, ALGORITHM
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kimlik bilgileri")
#         # Veritabanından kullanıcıyı getir
#         user_repo = UserRepository(db) # Varsayımsal UserRepository
#         user = await user_repo.get_by_username(username)
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")
#         return user
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz token")

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if not current_user.is_active:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Devre dışı bırakılmış kullanıcı")
#     return current_user