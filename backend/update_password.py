#!/usr/bin/env python3
"""
Обновление пароля в .env файле
"""
import os
import re

# Читаем текущий .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    print("ERROR: .env file not found")
    exit(1)

with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Запрашиваем пароль
print("Enter PostgreSQL password for user 'postgres':")
print("(Press Enter to use 'bossboard123')")
password = input().strip()
if not password:
    password = "bossboard123"

# Обновляем DATABASE_URL
# Формат: postgresql://postgres:password@5.tcp.eu.ngrok.io:14257/bossboard
pattern = r'DATABASE_URL=postgresql://postgres:[^@]+@'
replacement = f'DATABASE_URL=postgresql://postgres:{password}@'
new_content = re.sub(pattern, replacement, content)

# Сохраняем
with open(env_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"SUCCESS: Updated .env with password")
print(f"Now test connection with: python -c \"import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); print('Connection OK'); conn.close()\"")

