from fastapi import APIRouter, Depends, HTTPException
from src.db import get_db_connection
from src.dependencies import get_current_user
from src.schemas import CartItem, CartAddMultiple, Order

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/{order_id}", response_model=list[CartItem])
def get_cart(order_id: int, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    # Проверка: владелец или админ?
    cur.execute("SELECT user_id FROM frog_cafe.orders WHERE id = %s;", (order_id,))
    order = cur.fetchone()

    if not order:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Заказ не найден")

    is_admin = current_user["role_id"] == 0
    is_owner = order["user_id"] == current_user["user_id"]

    if not (is_admin or is_owner):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Нет доступа к заказу")

    # Получаем блюда из корзины
    cur.execute("""
        SELECT m.id, m.dish_name, m.image, m.description, m.is_available
        FROM frog_cafe.cart c
        JOIN frog_cafe.menu m ON c.menu_item = m.id
        WHERE c.order_id = %s
    """, (order_id,))

    items = cur.fetchall()
    cur.close()
    conn.close()
    return items

@router.post("/{order_id}", response_model=Order)
def add_multiple_to_cart(order_id: int, items: CartAddMultiple, current_user=Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Start transaction
        cur.execute("BEGIN;")

        # Check order exists and get its details
        cur.execute("""
            SELECT o.user_id, o.status_id, s.name as status
            FROM frog_cafe.orders o
            JOIN frog_cafe.order_statuses s ON o.status_id = s.id
            WHERE o.id = %s
            FOR UPDATE;
        """, (order_id,))
        order = cur.fetchone()

        if not order:
            raise HTTPException(
                status_code=404, 
                detail="А где?"
            )

        # Check permissions
        is_admin = current_user["role_id"] == 0
        is_owner = order["user_id"] == current_user["user_id"]

        if not (is_admin or is_owner):
            raise HTTPException(
                status_code=403, 
                detail="Нет доступа к заказу"
            )

        # Check order status
        if order["status"] != "Создан":
            raise HTTPException(
                status_code=400,
                detail="Нельзя добавить товары в заказ с текущим статусом"
            )

        # Check menu items availability
        for menu_item_id in items.menu_items:
            cur.execute("""
                SELECT id, dish_name, quantity_left, is_available
                FROM frog_cafe.menu
                WHERE id = %s
                FOR UPDATE;
            """, (menu_item_id,))
            menu_item = cur.fetchone()

            if not menu_item:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Я дико извиняюсь, а вы о чем вообще"
                )

            if not menu_item["is_available"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"А все, а надо было раньше"
                )

            if menu_item["quantity_left"] < 1:
                raise HTTPException(
                    status_code=400, 
                    detail=f"'{menu_item['dish_name']}' схавали"
                )

        # Add items to cart and update quantities
        for menu_item_id in items.menu_items:
            # Add to cart
            cur.execute("""
                INSERT INTO frog_cafe.cart (order_id, menu_item)
                VALUES (%s, %s);
            """, (order_id, menu_item_id))

            # Update quantity
            cur.execute("""
                UPDATE frog_cafe.menu
                SET quantity_left = quantity_left - 1
                WHERE id = %s;
            """, (menu_item_id,))

        # Get updated order details
        cur.execute("""
            WITH cart_items AS (
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
                GROUP BY m.id, m.dish_name, m.image, m.is_available, m.description, m.category, m.quantity_left
            )
            SELECT 
                o.id,
                o.created_at,
                s.name as status,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'id', ci.id,
                            'dish_name', ci.dish_name,
                            'image', ci.image,
                            'is_available', ci.is_available,
                            'description', ci.description,
                            'category', ci.category,
                            'quantity_left', ci.quantity_left,
                            'quantity', ci.quantity
                        )
                    ) FILTER (WHERE ci.id IS NOT NULL),
                    '[]'::json
                ) as items
            FROM frog_cafe.orders o
            JOIN frog_cafe.order_statuses s ON o.status_id = s.id
            LEFT JOIN cart_items ci ON true
            WHERE o.id = %s
            GROUP BY o.id, o.created_at, s.name;
        """, (order_id, order_id))

        updated_order = cur.fetchone()
        
        if not updated_order:
            raise HTTPException(
                status_code=500,
                detail="Не удалось получить обновленные данные заказа"
            )

        # Commit transaction
        conn.commit()
        return updated_order

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при добавлении товаров в корзину: {str(e)}"
        )
    finally:
        cur.close()
        conn.close()
