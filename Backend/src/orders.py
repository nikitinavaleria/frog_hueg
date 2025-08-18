from fastapi import APIRouter, Depends, HTTPException, status
from src.db import get_db_connection
from src.schemas import Order, OrderCreate, OrderStatusUpdate
from src.dependencies import get_current_user, require_role
import logging
from psycopg2.extras import RealDictCursor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])

# GET /api/orders — все авторизованные пользователи
@router.get("/", response_model=list[Order])
def get_orders(current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # First get all orders with their status
        cur.execute("""
            SELECT 
                o.id,
                o.created_at,
                s.name as status
            FROM frog_cafe.orders o
            JOIN frog_cafe.order_statuses s ON o.status_id = s.id
            ORDER BY o.created_at DESC;
        """)
        orders = cur.fetchall()

        # Then get items for each order
        for order in orders:
            cur.execute("""
                SELECT 
                    m.id,
                    m.dish_name,
                    m.image,
                    m.is_available,
                    m.description,
                    m.category,
                    m.quantity_left,
                    COUNT(*) as quantity
                FROM frog_cafe.cart c
                JOIN frog_cafe.menu m ON c.menu_item = m.id
                WHERE c.order_id = %s
                GROUP BY m.id, m.dish_name, m.image, m.is_available, 
                         m.description, m.category, m.quantity_left;
            """, (order["id"],))
            items = cur.fetchall()
            order["items"] = items or []

        return orders

    except Exception as e:
        logger.error(f"Error in get_orders: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении заказов: {str(e)}"
        )
    finally:
        cur.close()
        conn.close()

# POST /api/orders — создание заказа с автоматической жабой
@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Start transaction
        cur.execute("BEGIN;")

        # Get available toad
        cur.execute("""
            SELECT id FROM frog_cafe.toads 
            WHERE is_taken = false 
            ORDER BY id 
            LIMIT 1 
            FOR UPDATE;
        """)
        toad = cur.fetchone()
        toad_id = toad["id"] if toad else None

        if toad:
            # Mark toad as taken
            cur.execute("""
                UPDATE frog_cafe.toads 
                SET is_taken = true 
                WHERE id = %s;
            """, (toad_id,))

        # Get initial order status
        cur.execute("""
            SELECT id, name 
            FROM frog_cafe.order_statuses 
            WHERE name = 'Создан' 
            LIMIT 1;
        """)
        status = cur.fetchone()
        
        if not status:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось найти начальный статус заказа"
            )

        # Create order
        cur.execute("""
            INSERT INTO frog_cafe.orders (user_id, toad_id, status_id)
            VALUES (%s, %s, %s)
            RETURNING id, created_at;
        """, (current_user["user_id"], toad_id, status["id"]))

        new_order = cur.fetchone()
        
        if not new_order:
            raise HTTPException(
                status_code=500, 
                detail="Не удалось создать заказ"
            )

        # Commit transaction
        conn.commit()

        return {
            "id": new_order["id"],
            "created_at": new_order["created_at"],
            "status": status["name"],
            "items": []
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании заказа: {str(e)}"
        )
    finally:
        cur.close()
        conn.close()

# GET /api/orders/{id}
@router.get("/{order_id}", response_model=Order, dependencies=[Depends(require_role([0]))])
def get_order(order_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # сам заказ + статус
            cur.execute("""
                SELECT
                    o.id,
                    o.user_id,
                    o.toad_id,
                    o.status_id,
                    o.created_at,
                    os.name AS status_name
                FROM frog_cafe.orders o
                JOIN frog_cafe.order_statuses os ON os.id = o.status_id
                WHERE o.id = %s;
            """, (order_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Заказ не найден")

            # позиции заказа -> MenuItem
            cur.execute("""
                SELECT
                    m.id,
                    m.dish_name,
                    m.image,
                    m.is_available,
                    m.description,
                    m.category,
                    m.quantity_left
                FROM frog_cafe.cart c
                JOIN frog_cafe.menu m ON m.id = c.menu_item
                WHERE c.order_id = %s
                ORDER BY c.id;
            """, (order_id,))
            items = [dict(r) for r in cur.fetchall()]

        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "status": row["status_name"],
            "items": items
        }
    finally:
        conn.close()

# PUT /api/orders/{id}/status — все авторизованные пользователи
@router.put("/{order_id}/status", response_model=Order)
def update_order_status(order_id: int, update: OrderStatusUpdate, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if order exists
        cur.execute("""
            SELECT id, status_id 
            FROM frog_cafe.orders 
            WHERE id = %s;
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        # Update order status
        cur.execute("""
            UPDATE frog_cafe.orders
            SET status_id = %s
            WHERE id = %s
            RETURNING id, created_at;
        """, (update.status_id, order_id))

        updated = cur.fetchone()
        if not updated:
            raise HTTPException(status_code=500, detail="Не удалось обновить статус заказа")

        # Get the new status name
        cur.execute("""
            SELECT name 
            FROM frog_cafe.order_statuses 
            WHERE id = %s;
        """, (update.status_id,))
        status = cur.fetchone()

        if not status:
            raise HTTPException(status_code=500, detail="Не удалось получить новый статус")

        # Get order items
        cur.execute("""
            SELECT 
                m.id,
                m.dish_name,
                m.image,
                m.is_available,
                m.description,
                m.category,
                m.quantity_left,
                COUNT(*) as quantity
            FROM frog_cafe.cart c
            JOIN frog_cafe.menu m ON c.menu_item = m.id
            WHERE c.order_id = %s
            GROUP BY m.id, m.dish_name, m.image, m.is_available, 
                     m.description, m.category, m.quantity_left;
        """, (order_id,))
        items = cur.fetchall()

        conn.commit()

        return {
            "id": updated["id"],
            "created_at": updated["created_at"],
            "status": status["name"],
            "items": items or []
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in update_order_status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении статуса заказа: {str(e)}"
        )
    finally:
        cur.close()
        conn.close()

# DELETE /api/orders/{id} — удаление заказа
@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Check if order exists and get its status
        cur.execute("""
            SELECT o.id, o.toad_id, s.name as status
            FROM frog_cafe.orders o
            JOIN frog_cafe.order_statuses s ON o.status_id = s.id
            WHERE o.id = %s;
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        # Only allow deletion if status is "Выдан"
        if order["status"] != "Выдан":
            raise HTTPException(
                status_code=400,
                detail="Можно удалить только заказы со статусом 'Выдан'"
            )

        # Free the toad if it exists
        if order["toad_id"]:
            cur.execute("""
                UPDATE frog_cafe.toads 
                SET is_taken = false 
                WHERE id = %s;
            """, (order["toad_id"],))

        # Delete cart items first (due to foreign key constraint)
        cur.execute("DELETE FROM frog_cafe.cart WHERE order_id = %s;", (order_id,))

        # Delete the order
        cur.execute("DELETE FROM frog_cafe.orders WHERE id = %s RETURNING id;", (order_id,))
        deleted = cur.fetchone()

        if not deleted:
            raise HTTPException(status_code=500, detail="Не удалось удалить заказ")

        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Error in delete_order: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении заказа: {str(e)}"
        )
    finally:
        cur.close()
        conn.close()

    return  # FastAPI автоматически вернёт 204 No Content

# DELETE /api/orders — удаление всех заказов
@router.delete("/", status_code=204, dependencies=[Depends(get_current_user)])
def clear_orders():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Start transaction
        cur.execute("BEGIN;")

        # Delete all orders
        cur.execute("DELETE FROM frog_cafe.orders;")
        
        # Commit transaction
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при очистке заказов: {str(e)}"
        )
    finally:
        cur.close()
        conn.close()

    return  # FastAPI автоматически вернёт 204 No Content
