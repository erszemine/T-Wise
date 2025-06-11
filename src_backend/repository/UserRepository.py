# src/stok_yonetim_backend/repositories/user_repository.py
from beanie import PydanticObjectId
from typing import List, Optional
from datetime import datetime

from models_entity.User import User # User modelini import edin

class UserRepository:
    """
    Kullanıcılar (User) ile ilgili veritabanı CRUD operasyonlarını yönetir.
    """

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Tüm kullanıcıları sayfalama ile getirir.
        """
        return await User.find_all().skip(skip).limit(limit).to_list()

    async def get_by_id(self, user_id: PydanticObjectId) -> Optional[User]:
        """
        Belirli bir ID'ye sahip kullanıcıyı getirir.
        """
        return await User.get(user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Belirli bir kullanıcı adına sahip kullanıcıyı getirir.
        """
        return await User.find_one(User.username == username)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Belirli bir e-posta adresine sahip kullanıcıyı getirir.
        """
        return await User.find_one(User.email == email)

    async def create(self, user_data: dict) -> User:
        """
        Yeni bir kullanıcı oluşturur ve veritabanına kaydeder.
        user_data: Pydantic modelinden dönüştürülmüş bir dict olmalı (hashed_password içerir).
        """
        user = User(**user_data)
        await user.insert()
        return user

    async def update(self, user_id: PydanticObjectId, update_data: dict) -> Optional[User]:
        """
        Belirli bir ID'ye sahip kullanıcının bilgilerini günceller.
        update_data: Güncellenecek alanları içeren bir dict olmalı.
        """
        user = await self.get_by_id(user_id)
        if user:
            for key, value in update_data.items():
                setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            await user.save()
            return user
        return None

    async def delete(self, user_id: PydanticObjectId) -> int:
        """
        Belirli bir ID'ye sahip kullanıcıyı siler.
        """
        user = await self.get_by_id(user_id)
        if user:
            await user.delete()
            return 1
        return 0