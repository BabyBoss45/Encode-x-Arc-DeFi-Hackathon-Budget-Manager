# Как добавить ENTITY_SECRET в .env

## Текущее состояние файла

Ваш `backend/.env` файл содержит:
```
DATABASE_URL=postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard
JWT_SECRET_KEY=my-secret-key-change-in-production-12345
CIRCLE_API_KEY=test-key
CIRCLE_BASE_URL=https://api.circle.com/v1
```

## Что нужно добавить

Добавьте строку с ENTITY_SECRET в конец файла:

```env
ENTITY_SECRET=your_64_character_hex_secret_here
```

## Полный .env файл должен выглядеть так:

```env
DATABASE_URL=postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard
JWT_SECRET_KEY=my-secret-key-change-in-production-12345
CIRCLE_API_KEY=test-key
CIRCLE_BASE_URL=https://api.circle.com/v1
ENTITY_SECRET=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

## Важно:

1. **Без кавычек** - пишите напрямую: `ENTITY_SECRET=xxx`
2. **Без пробелов** вокруг `=`
3. **Ровно 64 hex символа** (0-9, a-f)
4. **На новой строке** в конце файла

## После добавления:

1. Сохраните файл
2. Проверьте: `python check_env_detailed.py`
3. Запустите транзакцию: `python send_transaction.py`

