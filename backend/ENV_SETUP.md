# Настройка .env файла

## Расположение файла

Создайте файл `backend/.env` в корне папки `backend`.

## Минимальный .env файл

```env
# База данных (PostgreSQL через ngrok или локально)
DATABASE_URL=postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard

# JWT секретный ключ
JWT_SECRET_KEY=my-secret-key-change-in-production-12345

# Circle API ключ
CIRCLE_API_KEY=TEST_API_KEY:your_actual_api_key_here

# Entity Secret (64 hex символа) - ОБЯЗАТЕЛЬНО для транзакций
ENTITY_SECRET=your_64_character_hex_secret_here

# USDC Token ID (опционально)
USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8

# ngrok Frontend URL (для CORS, если используете ngrok)
# FRONTEND_URL=https://your-frontend-ngrok-url.ngrok.io
```

## Где найти значения

### 1. DATABASE_URL
- **Локально:** `postgresql://postgres:admin@localhost:5432/bossboard`
- **Через ngrok:** `postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard`
- **SQLite (для тестов):** `sqlite:///./bossboard.db`

### 2. JWT_SECRET_KEY
- Любая случайная строка (минимум 32 символа)
- Пример: `my-super-secret-jwt-key-12345-change-in-production`

### 3. CIRCLE_API_KEY
- Circle Dashboard → API Keys
- Формат: `TEST_API_KEY:your_key` или `PROD_API_KEY:your_key`
- Если у вас только ключ без префикса, добавьте `TEST_API_KEY:` перед ним

### 4. ENTITY_SECRET (ВАЖНО!)
- Circle Dashboard → Developer Settings
- Должен быть ровно 64 hex символа (0-9, a-f)
- Пример: `0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef`
- **НЕ ДЕЛИТЕСЬ ЭТИМ КЛЮЧОМ!**

### 5. USDC_TOKEN_ID (опционально)
- Для ARC-TESTNET: `15dc2b5d-0994-58b0-bf8c-3a0501148ee8`
- Можно найти через API или оставить пустым (будет искаться автоматически)

### 6. FRONTEND_URL (опционально, для ngrok)
- URL вашего frontend ngrok туннеля
- Используется для настройки CORS в backend
- Формат: `https://xxxx-xx-xx-xx-xx.ngrok.io`
- См. `NGROK_SETUP.md` для подробностей

## Пример полного .env файла

```env
# Database
DATABASE_URL=postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard

# JWT
JWT_SECRET_KEY=my-secret-key-change-in-production-12345

# Circle API
CIRCLE_API_KEY=TEST_API_KEY:abc123def456ghi789
ENTITY_SECRET=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8

# ngrok Frontend URL (для CORS, если используете ngrok)
# Раскомментируйте и укажите ваш frontend ngrok URL
# FRONTEND_URL=https://your-frontend-ngrok-url.ngrok.io
```

## Проверка настроек

После создания `.env` файла, проверьте настройки:

```bash
cd backend
python check_env.py
```

## Безопасность

⚠️ **ВАЖНО:**
- Никогда не коммитьте `.env` файл в git!
- Файл `.env` уже должен быть в `.gitignore`
- `ENTITY_SECRET` - это секретный ключ, храните его в безопасности
- В production используйте переменные окружения сервера вместо файла

## Быстрый старт

1. Скопируйте пример:
   ```bash
   cd backend
   copy .env.example .env
   ```

2. Откройте `.env` и заполните реальными значениями

3. Проверьте:
   ```bash
   python check_env.py
   ```

4. Запустите backend:
   ```bash
   python main.py
   ```

