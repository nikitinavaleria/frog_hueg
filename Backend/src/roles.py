from fastapi import APIRouter, Depends, HTTPException, status
from src.db import get_db_connection
from src.schemas import Role, RoleCreate
from src.dependencies import require_role

# Prefix is added when the router is mounted under `/api` in `main.py`.
# Using `/api/roles` here produced paths like `/api/api/roles`.
# Correct prefix should not include `/api`.
router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", response_model=list[Role], dependencies=[Depends(require_role([0]))])
def get_roles():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM frog_cafe.roles ORDER BY id;")
    roles = cur.fetchall()
    cur.close()
    conn.close()
    return roles

@router.post("/", response_model=Role, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([0]))])
def create_role(role: RoleCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM frog_cafe.roles;")
    row = cur.fetchone()
    new_id = row["next_id"]

    cur.execute(
        "INSERT INTO frog_cafe.roles (id, name) VALUES (%s, %s) RETURNING id, name;",
        (new_id, role.name)
    )
    new_role = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_role

@router.get("/{role_id}", response_model=Role, dependencies=[Depends(require_role([0]))])
def get_role(role_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM frog_cafe.roles WHERE id = %s;", (role_id,))
    role = cur.fetchone()
    cur.close()
    conn.close()
    if not role:
        raise HTTPException(status_code=404, detail="Роль не найдена")
    return role

@router.put("/{role_id}", response_model=Role, dependencies=[Depends(require_role([0]))])
def update_role(role_id: int, role: RoleCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE frog_cafe.roles
        SET name = %s
        WHERE id = %s
        RETURNING id, name;
    """, (role.name, role_id))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Роль не найдена")
    return updated

@router.delete("/{role_id}", status_code=204, dependencies=[Depends(require_role([0]))])
def delete_role(role_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM frog_cafe.roles WHERE id = %s RETURNING id;", (role_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Роль не найдена")
    return
