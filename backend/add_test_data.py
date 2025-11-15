#!/usr/bin/env python3
"""
Скрипт для добавления тестовых данных в базу данных
"""
import psycopg2
import os
from dotenv import load_dotenv
from datetime import date, datetime
from passlib.context import CryptContext

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
    print("[ERROR] DATABASE_URL не настроен для PostgreSQL!")
    exit(1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("ADDING TEST DATA")
    print("=" * 80)
    
    # 1. Create user
    print("\n[1] Creating user...")
    password_hash = pwd_context.hash("test123")
    cursor.execute("""
        INSERT INTO users (email, password_hash, company_name, created_at)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (email) DO NOTHING
        RETURNING id
    """, ('test@example.com', password_hash, 'Test Company'))
    
    user_result = cursor.fetchone()
    if user_result:
        user_id = user_result[0]
        print(f"  [OK] User created with ID: {user_id}")
    else:
        cursor.execute("SELECT id FROM users WHERE email = %s", ('test@example.com',))
        user_id = cursor.fetchone()[0]
        print(f"  [INFO] User already exists with ID: {user_id}")
    
    # 2. Create company
    print("\n[2] Creating company...")
    cursor.execute("""
        INSERT INTO companies (user_id, master_wallet_address, payroll_date, payroll_time, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (user_id) DO NOTHING
        RETURNING id
    """, (user_id, '0x1234567890123456789012345678901234567890', date.today(), '09:00'))
    
    company_result = cursor.fetchone()
    if company_result:
        company_id = company_result[0]
        print(f"  [OK] Company created with ID: {company_id}")
    else:
        cursor.execute("SELECT id FROM companies WHERE user_id = %s", (user_id,))
        company_id = cursor.fetchone()[0]
        print(f"  [INFO] Company already exists with ID: {company_id}")
    
    # 3. Create departments
    print("\n[3] Creating departments...")
    departments = ['Engineering', 'Marketing', 'Sales', 'HR']
    dept_ids = {}
    for dept_name in departments:
        cursor.execute("""
            INSERT INTO departments (company_id, name, created_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (company_id, dept_name))
        
        result = cursor.fetchone()
        if result:
            dept_ids[dept_name] = result[0]
            print(f"  [OK] Department '{dept_name}' created with ID: {result[0]}")
        else:
            cursor.execute("SELECT id FROM departments WHERE company_id = %s AND name = %s", (company_id, dept_name))
            dept_ids[dept_name] = cursor.fetchone()[0]
            print(f"  [INFO] Department '{dept_name}' already exists")
    
    # 4. Create workers
    print("\n[4] Creating workers...")
    workers_data = [
        ('John', 'Doe', 5000.0, '0x1111111111111111111111111111111111111111', 'Engineering'),
        ('Jane', 'Smith', 6000.0, '0x2222222222222222222222222222222222222222', 'Marketing'),
        ('Bob', 'Johnson', 5500.0, '0x3333333333333333333333333333333333333333', 'Sales'),
        ('Alice', 'Williams', 5200.0, '0x4444444444444444444444444444444444444444', 'Engineering'),
        ('Charlie', 'Brown', 4800.0, '0x5555555555555555555555555555555555555555', 'HR'),
    ]
    
    for name, surname, salary, wallet, dept_name in workers_data:
        cursor.execute("""
            INSERT INTO workers (department_id, name, surname, salary, wallet_address, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
            RETURNING id
        """, (dept_ids[dept_name], name, surname, salary, wallet))
        worker_id = cursor.fetchone()[0]
        print(f"  [OK] Worker {name} {surname} created with ID: {worker_id}")
    
    # 5. Create spendings
    print("\n[5] Creating spendings...")
    spendings_data = [
        ('Office Supplies', 500.0, '0x7777777777777777777777777777777777777777', 'Marketing'),
        ('Software Licenses', 1200.0, '0x8888888888888888888888888888888888888888', 'Engineering'),
        ('Marketing Campaign', 3000.0, '0x9999999999999999999999999999999999999999', 'Marketing'),
    ]
    
    for name, amount, wallet, dept_name in spendings_data:
        cursor.execute("""
            INSERT INTO additional_spendings (company_id, department_id, name, amount, wallet_address, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (company_id, dept_ids[dept_name], name, amount, wallet))
        spending_id = cursor.fetchone()[0]
        print(f"  [OK] Spending '{name}' created with ID: {spending_id}")
    
    # 6. Create revenues
    print("\n[6] Creating revenues...")
    current_date = date.today()
    revenues_data = [
        (50000.0, current_date.month, current_date.year),
        (55000.0, (current_date.month - 1) or 12, current_date.year if current_date.month > 1 else current_date.year - 1),
        (60000.0, (current_date.month - 2) or (12 if current_date.month == 1 else 11), current_date.year if current_date.month > 2 else (current_date.year - 1 if current_date.month == 1 else current_date.year)),
    ]
    
    for amount, month, year in revenues_data:
        cursor.execute("""
            INSERT INTO revenues (company_id, amount, month, year, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT DO NOTHING
            RETURNING id
        """, (company_id, amount, month, year))
        result = cursor.fetchone()
        if result:
            print(f"  [OK] Revenue for {month}/{year}: {amount} created with ID: {result[0]}")
        else:
            print(f"  [INFO] Revenue for {month}/{year} already exists")
    
    conn.commit()
    
    # Statistics
    print("\n" + "=" * 80)
    print("STATISTICS:")
    print("=" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"  Users: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM companies")
    print(f"  Companies: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM departments")
    print(f"  Departments: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM workers")
    print(f"  Workers: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM additional_spendings")
    print(f"  Spendings: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM revenues")
    print(f"  Revenues: {cursor.fetchone()[0]}")
    
    conn.close()
    print("\n[OK] Test data successfully added!")
    print("\nLogin credentials:")
    print("  Email: test@example.com")
    print("  Password: test123")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    if conn:
        conn.rollback()
    exit(1)

