# src_backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime, timedelta, timezone
import os


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
    # full_name yerine first_name ve last_name
    first_name: str
    last_name: str
    email: Optional[str] = None
    position: str = "Depo Sorumlusu" # Varsayılan rol

# Veritabanı bağlantısı (database.py dosyasından connect_db fonksiyonu)
from database import connect_db

# Güvenlik ve kullanıcı modelleri
from security import create_access_token, authenticate_user, hash_password, get_current_user
from models_entity.User import User
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
        raise RuntimeError(f"Veritabanı bağlantısı kurulamadı: {e}") 

    yield

    print("Uygulama kapanıyor...")
    print("MongoDB bağlantısı kapatıldı (varsa).")


app = FastAPI(
    title="T-Wise Depo ve Stok Yönetim Sistemi API",
    description="FastAPI ve MongoDB ile geliştirilmiş basit envanter takip sistemi.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)
origins = [
    "http://localhost:8000", # Backend URL'si
    "http://localhost:8080", # BURADA SİZİN FRONTEND URL'İNİZ OLMALI!
    # Eğer frontend'i farklı bir portta (örn. 8002, 8003) test ederseniz, o URL'leri de buraya eklemelisiniz.
]

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hesap aktif değil")

    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Kullanıcı Kayıt Endpoint
@app.post("/api/register", status_code=status.HTTP_201_CREATED, summary="Yeni kullanıcı kaydı")
async def register_user(user_register: UserRegister):
    existing_user = await User.find_one(User.username == user_register.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kullanıcı adı zaten mevcut")

    if user_register.email:
        existing_email_user = await User.find_one(User.email == user_register.email)
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-posta adresi zaten kullanımda")

    hashed_password = hash_password(user_register.password)
    new_user = User(
        username=user_register.username,
        password_hash=hashed_password,
        first_name=user_register.first_name,
        last_name=user_register.last_name,
        email=user_register.email,
        position=user_register.position,
        is_active=True,
        created_at=datetime.utcnow() # created_at eklendi
    )
    await new_user.insert()
    return {"username": new_user.username, "message": "Kullanıcı başarıyla kaydedildi, lütfen giriş yapın."}


# --- Router'ları Uygulamaya Dahil Et ---
app.include_router(product_router)
app.include_router(stock_router)
app.include_router(stock_management_router)
app.include_router(user_router, prefix="/users", tags=["Users"])

# Varsayılan kök endpoint
@app.get("/", summary="API'nin ana kök dizini")
async def read_root():
    return {"message": "T-Wise Depo ve Stok Yönetim Sistemi API'sine hoş geldiniz!"}

# --- Global Hata Yakalayıcılar ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Doğrulama Hatası", "details": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Sunucu hatası oluştu.", "detail": str(exc)},
    )