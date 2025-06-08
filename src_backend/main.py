# src_backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import BaseModel, Field
from datetime import timedelta

from database import connect_db
from security import create_access_token, authenticate_user, hash_password, get_current_user
from models_entity.User import User
from bson.objectid import ObjectId # ObjectId'i kullanmak için

# API Router'larını import edin
from api.product_routes import router as product_router
from api.stock_routes import router as stock_router
from api.stock_management_routes import router as stock_management_router
from api.user_routes import router as user_router
# Üretim talebi ile ilgili routerlar buraya eklenmeyecek

# Pydantic Request/Response Modelleri (Login/Register için)
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

app = FastAPI(
    title="T-Wise Basit Envanter Yönetim Sistemi API",
    description="FastAPI ve MongoDB ile geliştirilmiş basit envanter takip sistemi.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme için hepsi, prod için belirli origin'ler
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uygulama başlarken DB bağlantısı
@app.on_event("startup")
async def on_startup():
    await connect_db()
    print("FastAPI uygulaması başladı ve MongoDB bağlantısı kuruldu.")

# Uygulama kapanırken (isteğe bağlı)
@app.on_event("shutdown")
async def on_shutdown():
    print("FastAPI uygulaması kapatıldı.")

# --- API Rotaları ---

# Login Endpoint
@app.post("/api/token", response_model=Token, summary="Kullanıcı girişi ve token alma")
async def login_for_access_token(user_login: UserLogin):
    user = await authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yanlış kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active: # Kullanıcının aktif olup olmadığını kontrol edin
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hesap aktif değil")

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Kullanıcı Kayıt Endpoint
# Not: İlk yönetici kullanıcıyı Compass'tan eklediyseniz, bu endpoint'i yetkilendirme ile koruyabilirsiniz.
# Örneğin: current_user: User = Depends(role_required(["Yönetici"])) ekleyerek
@app.post("/api/register", response_model=UserLogin, status_code=status.HTTP_201_CREATED, summary="Yeni kullanıcı kaydı")
async def register_user(user_register: UserRegister):
    # Mevcut kullanıcı kontrolü
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
        is_active=True # Yeni kullanıcılar varsayılan olarak aktif başlar
    )
    await new_user.insert()
    # Güvenlik nedeniyle şifreyi doğrudan geri döndürmeyin.
    # Sadece kaydedilen kullanıcı adını döndürelim.
    return {"username": new_user.username, "password": "User registered successfully, please login."}

# --- Router'ları Uygulamaya Dahil Et ---
app.include_router(product_router, prefix="/api/products", tags=["Products"])
app.include_router(stock_router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(stock_management_router, prefix="/api/stock-management", tags=["Stock Management"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])