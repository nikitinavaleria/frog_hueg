from fastapi import APIRouter, Depends, HTTPException, status
from src.db import get_db_connection
from src.schemas import Toad, ToadCreate
from src.dependencies import require_role

# This router is mounted under `/api`, so the prefix should not repeat it.
router = APIRouter(prefix="/toads", tags=["toads"])

@router.get("/", response_model=list[Toad], dependencies=[Depends(require_role([0]))])
def get_all_toads():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, pic, is_taken FROM frog_cafe.toads ORDER BY id;")
    toads = cur.fetchall()
    cur.close()
    conn.close()
    return toads

@router.post("/", response_model=Toad, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role([0]))])
def create_toad(toad: ToadCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO frog_cafe.toads (pic, is_taken) VALUES (%s, %s) RETURNING id, pic, is_taken;", (toad.pic, toad.is_taken))
    new_toad = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_toad

@router.get("/{toad_id}", response_model=Toad, dependencies=[Depends(require_role([0]))])
def get_toad(toad_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, pic, is_taken FROM frog_cafe.toads WHERE id = %s;", (toad_id,))
    toad = cur.fetchone()
    cur.close()
    conn.close()
    if not toad:
        raise HTTPException(status_code=404, detail="Жаба не найдена")
    return toad

@router.put("/{toad_id}", response_model=Toad, dependencies=[Depends(require_role([0]))])
def update_toad(toad_id: int, toad: ToadCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE frog_cafe.toads
        SET pic = %s, is_taken = %s
        WHERE id = %s
        RETURNING id, pic, is_taken;
    """, (toad.pic, toad.is_taken, toad_id))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Жаба не найдена")
    return updated

@router.delete("/{toad_id}", status_code=204, dependencies=[Depends(require_role([0]))])
def delete_toad(toad_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM frog_cafe.toads WHERE id = %s RETURNING id;", (toad_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail="Жаба не найдена")
    return
