#!/usr/bin/env python3
"""
Скрипт для установки пароля PostgreSQL
"""
import psycopg2
import sys

# Попробуем подключиться без пароля (если настроено trust)
# Или используйте известный пароль
try:
    # Попробуем подключиться к localhost без пароля
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password=""  # Пустой пароль или известный
    )
except:
    try:
        # Попробуем с паролем "postgres"
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="postgres"
        )
    except Exception as e:
        print("❌ Не удалось подключиться к PostgreSQL")
        print("Попробуйте один из вариантов:")
        print("1. Подключитесь через pgAdmin и измените пароль вручную")
        print("2. Или введите известный пароль:")
        password = input("Введите текущий пароль postgres (или Enter для пропуска): ")
        if password:
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    database="postgres",
                    user="postgres",
                    password=password
                )
            except:
                print("❌ Неверный пароль")
                sys.exit(1)
        else:
            sys.exit(1)

# Установим новый пароль
new_password = input("Введите новый пароль для postgres (или Enter для 'bossboard123'): ").strip()
if not new_password:
    new_password = "bossboard123"

try:
    cursor = conn.cursor()
    cursor.execute(f"ALTER USER postgres WITH PASSWORD '{new_password}';")
    conn.commit()
    print(f"✅ Пароль успешно изменен на: {new_password}")
    print(f"\nОбновите .env файл:")
    print(f"DATABASE_URL=postgresql://postgres:{new_password}@5.tcp.eu.ngrok.io:14257/bossboard")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка при изменении пароля: {e}")
    conn.close()

