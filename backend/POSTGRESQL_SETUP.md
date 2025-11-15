# Быстрая настройка PostgreSQL

## 1. Установка PostgreSQL

### Windows
Скачайте и установите с https://www.postgresql.org/download/windows/

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@14
```

## 2. Создание базы данных

```bash
# Войдите в PostgreSQL
psql -U postgres

# Создайте базу данных
CREATE DATABASE bossboard;

# Выйдите
\q
```

## 3. Создание таблиц

```bash
psql -U postgres -d bossboard -f postgresql_schema.sql
```

## 4. Настройка .env

Скопируйте `.env.example` в `.env` и заполните:

```env
DATABASE_URL=postgresql://postgres:ваш_пароль@localhost:5432/bossboard
JWT_SECRET_KEY=ваш-секретный-ключ
```

## 5. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 6. Запуск

```bash
python main.py
```

## Миграция данных из SQLite (если нужно)

```bash
python migrate_sqlite_to_postgres.py
```

## Использование облачной базы данных

### Heroku Postgres
1. Создайте приложение на Heroku
2. Добавьте PostgreSQL addon
3. Скопируйте DATABASE_URL из настроек

### Railway
1. Создайте проект на Railway
2. Добавьте PostgreSQL сервис
3. Скопируйте DATABASE_URL

### Supabase
1. Создайте проект на Supabase
2. Перейдите в Database settings
3. Скопируйте Connection string

### Neon
1. Создайте проект на Neon
2. Скопируйте Connection string

Все эти сервисы предоставляют бесплатный tier для начала работы!

