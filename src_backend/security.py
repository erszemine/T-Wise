from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES # <-- İşte burada kullanıyoruz!

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ... JWT token oluşturma, doğrulama vb. fonksiyonları ...