from fastapi import APIRouter, Depends, HTTPException, status
from src.db import get_db_connection
from src.schemas import MenuItem, MenuItemCreate
from src.dependencies import require_role, get_current_user
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable automatic trailing slash redirect
router = APIRouter(prefix="/menu", tags=["menu"])

# @router.get("", response_model=list[MenuItem])  # Route without trailing slash
@router.get("/", response_model=list[MenuItem])  # Route with trailing slash
def get_menu():
    try:
        logger.info("Attempting to connect to database...")
        conn = get_db_connection()
        cur = conn.cursor()
        
        logger.info("Executing menu query...")
        cur.execute("SELECT * FROM frog_cafe.menu ORDER BY id;")
        rows = cur.fetchall()
        
        logger.info(f"Found {len(rows)} menu items")
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Error in get_menu: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/", response_model=MenuItem)
def create_menu_item(
    item: MenuItemCreate,
    current_user: dict = Depends(require_role([0]))
):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM frog_cafe.menu WHERE dish_name = %s", (item.dish_name,))
    existing_item = cur.fetchone()
    if existing_item:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Блюдо с таким названием уже существует")

    cur.execute("""
        INSERT INTO frog_cafe.menu 
        (dish_name, image, is_available, description, category, quantity_left)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, dish_name, image, is_available, description, category, quantity_left;
    """, (
        item.dish_name,
        item.image,
        item.is_available,
        item.description,
        item.category,
        item.quantity_left
    ))

    new_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"User {current_user['name']} added new dish: {item.dish_name}")
    return new_item





@router.get("/{item_id}", response_model=MenuItem)
def get_menu_item(item_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM frog_cafe.menu WHERE id = %s", (item_id,))
    item = cur.fetchone()

    cur.close()
    conn.close()

    if not item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return item





@router.put("/{item_id}", response_model=MenuItem, dependencies=[Depends(get_current_user)])
def update_menu_item(item_id: int, item: MenuItemCreate):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE frog_cafe.menu
        SET dish_name = %s,
            image = %s,
            is_available = %s,
            description = %s,
            category = %s,
            quantity_left = %s
        WHERE id = %s
        RETURNING id, dish_name, image, is_available, description, category, quantity_left;
    """, (item.dish_name, item.image, item.is_available, item.description, item.category, item.quantity_left, item_id))

    updated_item = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not updated_item:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return updated_item



@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role([0]))])
def delete_menu_item(item_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM frog_cafe.menu WHERE id = %s RETURNING id;", (item_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return