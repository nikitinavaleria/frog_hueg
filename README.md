# frog hueg

Мини-приложение для весёлого ужина с друзьями.
Позвольте друзьям выбрать позиции из вашего жабьего меню.

В решении реализованы страницы
- выбора блюд,
- вывода на телевизор статуса готовности заказа
- админской панели, где можно двигать заказы и редактировать их наличие

## Референсы проекта
- Презентации стиля 2000х
- Жабий нейминг
- Вайб кринжпати
- Comic Sans

## Развитие
- Выдача картинки жабы при оформлении для идентификации при выдаче заказа
- Страница с мемами пока пользователь ждет заказ

## Запуск через Docker

1. Создайте файл `.env` в корне проекта и укажите параметры:


2. Соберите и запустите контейнеры:

```bash
docker compose up --build
```

Адреса сервисов можно изменить через `BACKEND_PORT` и `FRONTEND_PORT` в `.env`.
По умолчанию backend будет доступен на `http://localhost:8000`, frontend — на `http://localhost:5173`.

## Документация

http://localhost:8000/api/docs

