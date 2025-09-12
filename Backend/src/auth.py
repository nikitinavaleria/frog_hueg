from fastapi import APIRouter, Depends, HTTPException
import logging
from src.db import get_db_connection
from src.schemas import UserResponse, LoginRequest, TokenResponse
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

router = APIRouter()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Секрет и алгоритм для JWT
SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key_here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/auth/login/", response_model=TokenResponse)
def login(login_data: LoginRequest):
    logger.info(f"Login attempt - username: {login_data.username}")
    conn = get_db_connection()
    cur = conn.cursor()
    query = "SELECT * FROM frog_cafe.users WHERE name = %s"
    cur.execute(query, (login_data.username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user or not bcrypt.checkpw(login_data.password.encode("utf-8"), user["pass"].encode("utf-8")):
        logger.warning(f"Invalid credentials for user: {login_data.username}")
        raise HTTPException(status_code=401, detail="Вы кто такой? Я вас не звал")
    # Генерируем JWT-токен
    access_token = create_access_token({
        "sub": str(user["id"]),
        "name": user["name"],
        "role_id": user["role_id"]
    })
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "role_id": user["role_id"]
}