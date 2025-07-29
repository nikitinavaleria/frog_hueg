from fastapi import HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET", "your_secret_key_here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        name: str = payload.get("name")
        role_id: int = payload.get("role_id")
        if user_id is None or name is None or role_id is None:
            raise credentials_exception
        return {"user_id": int(user_id), "name": name, "role_id": role_id}
    except JWTError:
        raise credentials_exception

# Проверка доступа по ролям
def require_role(allowed_roles: list[int]):
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["role_id"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return current_user
    return checker 