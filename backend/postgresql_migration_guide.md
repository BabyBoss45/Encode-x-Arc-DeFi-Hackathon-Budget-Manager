# Миграция на PostgreSQL

Это руководство поможет вам перейти с SQLite на PostgreSQL для запуска базы данных в интернете.

## Шаг 1: Установка PostgreSQL

### Windows
1. Скачайте PostgreSQL с официального сайта: https://www.postgresql.org/download/windows/
2. Установите PostgreSQL (запомните пароль для пользователя `postgres`)
3. PostgreSQL будет доступен на порту 5432

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### macOS
```bash
brew install postgresql@14
brew services start postgresql@14
```

## Шаг 2: Создание базы данных

### Вариант A: Через командную строку
```bash
# Войдите в PostgreSQL
psql -U postgres

# Создайте базу данных
CREATE DATABASE bossboard;

# Создайте пользователя (опционально, для безопасности)
CREATE USER bossboard_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE bossboard TO bossboard_user;

# Выйдите
\q
```

### Вариант B: Через pgAdmin (GUI)
1. Откройте pgAdmin
2. Создайте новую базу данных с именем `bossboard`
3. Сохраните

## Шаг 3: Создание таблиц

Выполните SQL скрипт для создания всех таблиц:

```bash
# Через командную строку
psql -U postgres -d bossboard -f backend/postgresql_schema.sql

# Или через psql интерактивно
psql -U postgres -d bossboard
\i backend/postgresql_schema.sql
```

## Шаг 4: Установка зависимостей Python

```bash
cd backend
pip install psycopg2-binary
```

Или обновите `requirements.txt` (уже сделано) и установите:
```bash
pip install -r requirements.txt
```

## Шаг 5: Настройка переменных окружения

Создайте файл `.env` в папке `backend/`:

```env
# PostgreSQL connection string
# Формат: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/bossboard

# Или если используете отдельного пользователя:
# DATABASE_URL=postgresql://bossboard_user:your_secure_password@localhost:5432/bossboard

# JWT Secret Key (измените на случайную строку!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Circle API (опционально)
CIRCLE_API_KEY=your-circle-api-key
CIRCLE_BASE_URL=https://api.circle.com/v1
```

## Шаг 6: Миграция данных из SQLite (если нужно)

Если у вас уже есть данные в SQLite, используйте скрипт миграции:

```bash
python backend/migrate_sqlite_to_postgres.py
```

## Шаг 7: Запуск приложения

```bash
cd backend
python main.py
```

Приложение должно подключиться к PostgreSQL вместо SQLite.

## Использование облачной базы данных

### Heroku Postgres
1. Создайте приложение на Heroku
2. Добавьте PostgreSQL addon
3. Получите DATABASE_URL из переменных окружения Heroku
4. Используйте этот URL в `.env`

### AWS RDS
1. Создайте PostgreSQL инстанс в AWS RDS
2. Получите connection string
3. Используйте в `.env`

### Railway, Supabase, Neon, и другие
1. Создайте PostgreSQL базу данных
2. Получите connection string
3. Используйте в `.env`

## Формат DATABASE_URL

```
postgresql://[user[:password]@][host][:port][/database][?param1=value1&...]
```

Примеры:
- Локально: `postgresql://postgres:password@localhost:5432/bossboard`
- Heroku: `postgresql://user:pass@host:5432/dbname`
- Cloud: `postgresql://user:pass@host.amazonaws.com:5432/dbname`

## Проверка подключения

```python
# Тестовый скрипт
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Подключение к PostgreSQL успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
```

## Откат на SQLite (если нужно)

Просто измените `DATABASE_URL` в `.env`:
```env
DATABASE_URL=sqlite:///./bossboard.db
```

