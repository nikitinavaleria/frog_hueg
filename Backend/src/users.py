from fastapi import APIRouter, Depends, HTTPException
from src.db import get_db_connection
from src.schemas import User, UserCreate
from src.dependencies import require_role

# Routers are mounted under `/api` in `main.py`; using `/api/users` here
# resulted in paths like `/api/api/users`. Use a relative prefix instead.
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[User], dependencies=[Depends(require_role([0]))])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, role_id FROM frog_cafe.users ORDER BY id")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users


@router.post("/", response_model=User, dependencies=[Depends(require_role([0]))])
def create_user(user: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    # Проверка, существует ли пользователь с таким именем
    cur.execute("SELECT * FROM frog_cafe.users WHERE name = %s", (user.name,))
    existing = cur.fetchone()

    if existing:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

    # Вставка нового пользователя
    cur.execute("""
        INSERT INTO frog_cafe.users (name, pass, role_id)
        VALUES (%s, %s, %s)
        RETURNING id, name, role_id
    """, (user.name, user.password, user.role_id))

    new_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return new_user



@router.get("/{user_id}", response_model=User, dependencies=[Depends(require_role([0]))])
def get_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, role_id FROM frog_cafe.users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user



@router.put("/{user_id}", response_model=User, dependencies=[Depends(require_role([0]))])
def update_user(user_id: int, updated: UserCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    # Проверим, существует ли пользователь
    cur.execute("SELECT * FROM frog_cafe.users WHERE id = %s", (user_id,))
    existing = cur.fetchone()

    if not existing:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем пользователя
    cur.execute("""
        UPDATE frog_cafe.users
        SET name = %s, pass = %s, role_id = %s
        WHERE id = %s
        RETURNING id, name, role_id;
    """, (updated.name, updated.password, updated.role_id, user_id))

    user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return user



@router.delete("/{user_id}", status_code=204, dependencies=[Depends(require_role([0]))])
def delete_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM frog_cafe.users WHERE id = %s RETURNING id", (user_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return  # FastAPI автоматически вернёт 204 No Content
