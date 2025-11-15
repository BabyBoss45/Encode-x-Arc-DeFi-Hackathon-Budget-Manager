#!/usr/bin/env python3
"""
Миграция данных из SQLite в PostgreSQL
Запустите этот скрипт после создания таблиц в PostgreSQL
"""
import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite database
SQLITE_DB = "bossboard.db"

# PostgreSQL connection
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL or not POSTGRES_URL.startswith("postgresql"):
    print("❌ DATABASE_URL не настроен для PostgreSQL!")
    print("Установите DATABASE_URL в .env файле")
    exit(1)

def migrate_table(sqlite_conn, pg_conn, table_name, columns):
    """Мигрирует таблицу из SQLite в PostgreSQL"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        # Получить данные из SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"  ⚠️  Таблица {table_name} пуста, пропускаем")
            return
        
        # Вставить данные в PostgreSQL
        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)
        
        # Пропустить id для автоинкремента (если есть)
        if "id" in columns:
            id_index = columns.index("id")
            insert_columns = [c for c in columns if c != "id"]
            placeholders = ", ".join(["%s"] * len(insert_columns))
            columns_str = ", ".join(insert_columns)
            
            for row in rows:
                row_data = [val for i, val in enumerate(row) if i != id_index]
                pg_cursor.execute(
                    f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                    row_data
                )
        else:
            for row in rows:
                pg_cursor.execute(
                    f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                    row
                )
        
        pg_conn.commit()
        print(f"  ✅ Мигрировано {len(rows)} записей из {table_name}")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"  ❌ Ошибка при миграции {table_name}: {e}")
        raise

def main():
    print("🚀 Начало миграции данных из SQLite в PostgreSQL...")
    
    # Проверка SQLite базы
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Файл {SQLITE_DB} не найден!")
        return
    
    # Подключение к SQLite
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        print(f"✅ Подключено к SQLite: {SQLITE_DB}")
    except Exception as e:
        print(f"❌ Ошибка подключения к SQLite: {e}")
        return
    
    # Подключение к PostgreSQL
    try:
        pg_conn = psycopg2.connect(POSTGRES_URL)
        print(f"✅ Подключено к PostgreSQL")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        print("Проверьте DATABASE_URL в .env файле")
        sqlite_conn.close()
        return
    
    # Определение таблиц и их колонок (в порядке зависимостей)
    tables = [
        ("users", ["id", "email", "password_hash", "company_name", "created_at"]),
        ("companies", ["id", "user_id", "master_wallet_address", "payroll_date", "payroll_time", "created_at"]),
        ("departments", ["id", "company_id", "name", "created_at"]),
        ("workers", ["id", "department_id", "name", "surname", "salary", "wallet_address", "is_active", "created_at"]),
        ("additional_spendings", ["id", "company_id", "department_id", "name", "amount", "wallet_address", "created_at"]),
        ("revenues", ["id", "company_id", "amount", "month", "year", "created_at"]),
        ("payroll_transactions", ["id", "company_id", "worker_id", "amount", "period_start", "period_end", "status", "transaction_hash", "created_at"]),
        ("spending_transactions", ["id", "spending_id", "amount", "transaction_hash", "status", "created_at"]),
    ]
    
    try:
        for table_name, columns in tables:
            print(f"\n📦 Миграция таблицы: {table_name}")
            migrate_table(sqlite_conn, pg_conn, table_name, columns)
        
        print("\n✅ Миграция завершена успешно!")
        print("Теперь можно использовать PostgreSQL вместо SQLite")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время миграции: {e}")
    
    finally:
        sqlite_conn.close()
        pg_conn.close()
        print("\n🔌 Соединения закрыты")

if __name__ == "__main__":
    main()

