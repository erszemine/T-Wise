# src_backend/security.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models_entity.User import User
from beanie import PydanticObjectId 
from enums import UserPosition

load_dotenv() # .env dosyasını yükler

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY ortam değişkeni ayarlanmamış.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await User.get(PydanticObjectId(user_id)) # Değişiklik: ObjectId yerine PydanticObjectId
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

async def authenticate_user(username: str, password: str) -> Optional[User]:
    user = await User.find_one(User.username == username)
    if user: # Kullanıcı bulunduysa şifreyi doğrula
        if verify_password(password, user.password_hash):
            return user
    return None # Kullanıcı bulunamazsa veya şifre yanlışsa None döndürür

def role_required(required_positions: List[UserPosition]): # Parametre tipi UserPosition listesi oldu
    async def _role_checker(current_user: User = Depends(get_current_user)): # async eklendi
        if current_user.position not in required_positions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu işlemi gerçekleştirmek için yetkiniz yok." # Detay mesajı daha açıklayıcı
            )
        return current_user
    return _role_checker