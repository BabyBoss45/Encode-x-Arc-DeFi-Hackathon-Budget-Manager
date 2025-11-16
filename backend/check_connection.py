#!/usr/bin/env python3
"""
Проверка подключения к базе данных и отображение информации
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 80)
print("DATABASE CONNECTION INFO")
print("=" * 80)
print(f"\nDATABASE_URL: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Database info
    cursor.execute("SELECT current_database(), current_user, version()")
    db_info = cursor.fetchone()
    print(f"\nDatabase: {db_info[0]}")
    print(f"User: {db_info[1]}")
    print(f"PostgreSQL Version: {db_info[2][:50]}...")
    
    # Connection info
    cursor.execute("SELECT inet_server_addr(), inet_server_port()")
    server_info = cursor.fetchone()
    print(f"\nServer Address: {server_info[0]}")
    print(f"Server Port: {server_info[1]}")
    
    # Check data
    print("\n" + "=" * 80)
    print("DATA CHECK")
    print("=" * 80)
    
    tables = ['users', 'companies', 'departments', 'workers', 'additional_spendings', 'revenues']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
            
            if count > 0 and table == 'users':
                cursor.execute("SELECT id, email, company_name FROM users LIMIT 5")
                users = cursor.fetchall()
                print("    Sample users:")
                for u in users:
                    print(f"      ID: {u[0]}, Email: {u[1]}, Company: {u[2]}")
        except Exception as e:
            print(f"  {table}: ERROR - {e}")
    
    conn.close()
    print("\n[OK] Connection successful!")
    
except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
    exit(1)

