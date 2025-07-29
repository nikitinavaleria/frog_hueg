import bcrypt
from src.db import get_db_connection


def migrate():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, pass FROM frog_cafe.users")
    users = cur.fetchall()
    for user in users:
        hashed = bcrypt.hashpw(user["pass"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cur.execute("UPDATE frog_cafe.users SET pass = %s WHERE id = %s", (hashed, user["id"]))
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    migrate()

