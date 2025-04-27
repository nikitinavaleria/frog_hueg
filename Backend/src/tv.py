from fastapi import APIRouter, Depends, HTTPException
from src.db import get_db_connection
from src.schemas import TVOrder, TVDisplay
from src.dependencies import get_current_user, require_role
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tv", tags=["tv"])

@router.get("/display", response_model=TVDisplay)
def get_display_data(current_user=Depends(get_current_user)):
    logger.info(f"TV display request from user: {current_user}")
    
    if current_user["role_id"] not in [0, 2]:
        logger.warning(f"Unauthorized access attempt by user with role_id: {current_user['role_id']}")
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get active orders with their items
        query = """
            SELECT 
                o.id,
                o.created_at,
                s.name AS status,
                json_agg(
                    json_build_object(
                        'id', m.id,
                        'dish_name', m.dish_name,
                        'quantity', COUNT(m.id)
                    )
                ) AS items
            FROM frog_cafe.orders o
            JOIN frog_cafe.order_statuses s ON o.status_id = s.id
            JOIN frog_cafe.cart c ON o.id = c.order_id
            JOIN frog_cafe.menu m ON c.menu_item = m.id
            WHERE s.name != 'Выдан'
            GROUP BY o.id, o.created_at, s.name
            ORDER BY o.created_at DESC
        """
        logger.info("Executing query: %s", query)
        cur.execute(query)

        orders = cur.fetchall()
        logger.info(f"Found {len(orders)} orders")
        
        cur.close()
        conn.close()

        return {"orders": orders}
    except Exception as e:
        logger.error(f"Error in get_display_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders", response_model=list[TVOrder])
def get_tv_orders(current_user=Depends(get_current_user)):
    if current_user["role_id"] not in [0, 2]:
        logger.warning(f"Unauthorized access attempt by user with role_id: {current_user['role_id']}")
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            WITH order_items AS (
                SELECT 
                    o.id as order_id,
                    m.dish_name,
                    COUNT(*) as quantity
                FROM frog_cafe.orders o
                JOIN frog_cafe.order_statuses s ON o.status_id = s.id
                JOIN frog_cafe.cart c ON o.id = c.order_id
                JOIN frog_cafe.menu m ON c.menu_item = m.id
                WHERE s.name IN ('Готовится', 'Готов')
                GROUP BY o.id, m.dish_name
            )
            SELECT 
                o.id,
                o.created_at,
                s.name as status,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'dish_name', oi.dish_name,
                            'quantity', oi.quantity
                        )
                    ) FILTER (WHERE oi.dish_name IS NOT NULL),
                    '[]'::json
                ) as items
            FROM frog_cafe.orders o
            JOIN frog_cafe.order_statuses s ON o.status_id = s.id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE s.name IN ('Готовится', 'Готов')
            GROUP BY o.id, o.created_at, s.name
            ORDER BY o.created_at ASC;
        """)
        orders = cur.fetchall()
        cur.close()
        conn.close()
        
        # Преобразуем пустые массивы в пустые списки
        for order in orders:
            if not order['items']:
                order['items'] = []
                
        return orders
    except Exception as e:
        logger.error(f"Error in get_tv_orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
