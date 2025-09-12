from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth import router as auth_router
from src.menu import router as menu_router
from src.users import router as users_router
from src.roles import router as roles_router
from src.order_statuses import router as status_router
from src.toads import router as toads_router
from src.orders import router as orders_router
from src.cart import router as cart_router
from src.tv import router as tv_router

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Disable automatic trailing slash redirect
app = FastAPI(redirect_slashes=False)

# Configure CORS
# Адреса фронтенда и бэкенда можно задать через переменные окружения
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8378")
backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

origins = [
    frontend_url,
    backend_url,
    "*", 
]


app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400, 
)
api_app = FastAPI(title="API")

api_app.include_router(auth_router)
api_app.include_router(menu_router)
api_app.include_router(users_router)
api_app.include_router(roles_router)
api_app.include_router(status_router)
api_app.include_router(toads_router)
api_app.include_router(orders_router)
api_app.include_router(cart_router)
api_app.include_router(tv_router)

# Mount the API app under /api
app.mount("/api", api_app)

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run("src.main:app", host="172.20.10.2", port=8000, reload=True)
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

