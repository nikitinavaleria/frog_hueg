from fastapi import HTTPException, Depends

def get_current_user():
    # Для упрощения просто возвращаем тестового пользователя с ролью admin
    return {
        "user_id": 1,
        "name": "test",
        "role_id": 0  # admin role
    }

# Проверка доступа по ролям
def require_role(allowed_roles: list[int]):
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["role_id"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return current_user
    return checker 