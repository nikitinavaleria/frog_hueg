## API

### Переменные окружения

- SECRET_KEY — секретный ключ для подписи JWT (обязательно задать в .env для продакшена)

### **Аутентификация (JWT)**

POST /auth/login
- Принимает: {"username": "string", "password": "string"}
- Возвращает: {"access_token": "<JWT>", "token_type": "bearer"}
- Используйте access_token как Bearer-токен в заголовке Authorization для всех защищённых эндпоинтов.

Пример:

```
POST /auth/login
{
  "username": "admin",
  "password": "password"
}

Ответ:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer"
}
```

### **Menu:**

GET /api/menu - получение списка блюд

POST /api/menu - создание нового блюда

GET /api/menu/{item_id} - получение записи блюда

PUT /api/menu/{item_id} - редактирование записи блюда

DELETE /api/menu/{item_id} - удаление записи блюда

### **Users:**

GET /api/users - получение списка пользователей

POST /api/users - создание новой записи пользователя

GET /api/users/{user_id} - получение записи пользователя

PUT /api/users/{user_id} - редактирование записи пользователя

DELETE /api/users/{user_id} - удаление записи пользователя

### **Roles:**

GET /api/roles - получение списка ролей

POST /api/roles - создание роли

GET /api/roles/{role_id} - получение роли

PUT /api/roles/{role_id} - редактирование роли

DELETE /api/roles/{role_id} - удаление роли

### **Order_statuses:**

GET /api/order_statuses - получение списка статусов заказов

POST /api/order_statuses - создание нового статуса

GET /api/order_statuses/{status_id} - получение статуса

PUT /api/order_statuses/{status_id} - редактирование статуса

DELETE /api/order_statuses/{status_id} - удаление статуса

### **Toads:**

GET /api/toads - получение списка жабок

POST /api/toads - создание жабки

GET /api/toads/{toad_id} - получение жабки

PUT /api/toads/{toad_id} - редактирование жабки

DELETE /api/toads/{toad_id} - удаление жабки

### **Orders:**

GET /api/orders - получение списка заказов

POST /api/orders - создание заказа

DELETE /api/orders/ - удаление всех заказов

GET /api/orders/{order_id} - получение данных заказа

DELETE /api/orders/{order_id} - удаление заказа

PUT /api/orders/{order_id}/status - обновление статуса заказа отдельно

### **Cart:** 

GET /api/cart/{order_id} - получение списка блюд в заказе

POST /api/cart/{order_id} — добавляет блюда

### **TV:**

GET /api/tv/orders - вывод заказов на экран



