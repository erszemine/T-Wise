# src_backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from typing import Optional
from pydantic import BaseModel, Field
from datetime import timedelta, timezone

# --- Pydantic Request/Response Modelleri (Login/Register için) ---
# BU MODELLER DİĞER KÜTÜPHANE İMPORTLARINDAN VE FastAPI UYGULAMASI TANIMINDAN ÖNCE OLMALIDIR.
# KULLANILDIKLARI FONKSİYONLARDAN ÖNCE DE OLMALIDIR.
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str
    email: Optional[str] = None
    role: str = "Depo Sorumlusu" # Varsayılan rol

# Veritabanı bağlantısı
from database import connect_db

# Güvenlik ve kullanıcı modelleri
from security import create_access_token, authenticate_user, hash_password, get_current_user
from models_entity.User import User # Sadece User modelini import edin, UserLogin ve UserRegister burada tanımlı.
from beanie import PydanticObjectId

# API Router'larını import edin
from api.product_routes import router as product_router
from api.stock_routes import router as stock_router
from api.stock_management_routes import router as stock_management_router
from api.user_routes import router as user_router


# Uygulama yaşam döngüsü yöneticisi
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Uygulama başlıyor...")
    try:
        await connect_db()
        print("MongoDB bağlantısı başarılı.")
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {e}")
        # raise Exception(f"Veritabanı bağlantı hatası: {e}")

    yield

    print("Uygulama kapanıyor...")
    print("MongoDB bağlantısı kapatıldı (varsa).")


app = FastAPI(
    title="T-Wise Basit Envanter Yönetim Sistemi API",
    description="FastAPI ve MongoDB ile geliştirilmiş basit envanter takip sistemi.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Rotaları ---

# Login Endpoint
@app.post("/api/token", response_model=Token, summary="Kullanıcı girişi ve token alma")
async def login_for_access_token(user_login: UserLogin): # Bu satırda UserLogin kullanılır
    user = await authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yanlış kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hesap aktif değil")

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Kullanıcı Kayıt Endpoint
@app.post("/api/register", status_code=status.HTTP_201_CREATED, summary="Yeni kullanıcı kaydı")
async def register_user(user_register: UserRegister): # Bu satırda UserRegister kullanılır
    existing_user = await User.find_one(User.username == user_register.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kullanıcı adı zaten mevcut")

    hashed_password = hash_password(user_register.password)
    new_user = User(
        username=user_register.username,
        password_hash=hashed_password,
        full_name=user_register.full_name,
        email=user_register.email,
        role=user_register.role,
        is_active=True
    )
    await new_user.insert()
    return {"username": new_user.username, "message": "User registered successfully, please login."}

# --- Router'ları Uygulamaya Dahil Et ---
app.include_router(product_router, prefix="/api/products", tags=["Products"])
app.include_router(stock_router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(stock_management_router, prefix="/api/stock-management", tags=["Stock Management"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])

# Varsayılan kök endpoint
@app.get("/")
async def read_root():
    return {"message": "T-Wise Depo ve Stok Yönetim Sistemi API'sine hoş geldiniz!"}