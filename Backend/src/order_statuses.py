from fastapi import APIRouter, Depends, HTTPException, status
from src.db import get_db_connection
from src.schemas import OrderStatus, OrderStatusCreate
from src.dependencies import require_role

# This router is mounted under `/api` in `main.py`. Removing the redundant
# `/api` avoids paths like `/api/api/order_statuses`.
router = APIRouter(prefix="/order_statuses", tags=["order_statuses"])

@router.get("/", response_model=list[OrderStatus], dependencies=[Depends(require_role([0]))])
def get_statuses():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM frog_cafe.order_statuses ORDER BY id")
    statuses = cur.fetchall()
    cur.close()
    conn.close()
    return statuses

@router.post("/", response_model=OrderStatus, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([0]))])
def create_status(status: OrderStatusCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO frog_cafe.order_statuses (name) VALUES (%s) RETURNING id, name;", (status.name,))
    new_status = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_status

@router.get("/{status_id}", response_model=OrderStatus, dependencies=[Depends(require_role([0]))])
def get_status(status_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM frog_cafe.order_statuses WHERE id = %s;", (status_id,))
    status_item = cur.fetchone()
    cur.close()
    conn.close()
    if not status_item:
        raise HTTPException(status_code=404, detail="Статус не найден")
    return status_item

@router.put("/{status_id}", response_model=OrderStatus, dependencies=[Depends(require_role([0]))])
def update_status(status_id: int, status_data: OrderStatusCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE frog_cafe.order_statuses
        SET name = %s
        WHERE id = %s
        RETURNING id, name;
    """, (status_data.name, status_id))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Статус не найден")
    return updated

@router.delete("/{status_id}", status_code=204, dependencies=[Depends(require_role([0]))])
def delete_status(status_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM frog_cafe.order_statuses WHERE id = %s RETURNING id;", (status_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Статус не найден")
    return
