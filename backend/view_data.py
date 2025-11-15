#!/usr/bin/env python3
"""
Скрипт для просмотра данных в PostgreSQL через Python
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
    print("❌ DATABASE_URL не настроен для PostgreSQL!")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("ПРОСМОТР ДАННЫХ В БАЗЕ ДАННЫХ")
    print("=" * 80)
    
    # 1. Пользователи
    print("\n[1] ПОЛЬЗОВАТЕЛИ:")
    cursor.execute("SELECT id, email, company_name, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    if users:
        print(f"  {'ID':<5} {'Email':<30} {'Company Name':<25} {'Created At':<20}")
        print("  " + "-" * 80)
        for u in users:
            print(f"  {u[0]:<5} {u[1]:<30} {u[2]:<25} {str(u[3]):<20}")
    else:
        print("  Нет пользователей")
    
    # 2. Компании
    print("\n[2] КОМПАНИИ:")
    cursor.execute("""
        SELECT c.id, u.email, u.company_name, c.master_wallet_address, c.payroll_date, c.payroll_time
        FROM companies c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    """)
    companies = cursor.fetchall()
    if companies:
        print(f"  {'ID':<5} {'Email':<30} {'Company':<20} {'Wallet':<45} {'Payroll Date':<15}")
        print("  " + "-" * 120)
        for c in companies:
            wallet = str(c[3])[:42] + "..." if c[3] and len(str(c[3])) > 42 else (c[3] or "N/A")
            print(f"  {c[0]:<5} {c[1]:<30} {c[2]:<20} {wallet:<45} {str(c[4] or 'N/A'):<15}")
    else:
        print("  Нет компаний")
    
    # 3. Департаменты
    print("\n[3] ДЕПАРТАМЕНТЫ:")
    cursor.execute("""
        SELECT d.id, u.company_name, d.name, d.created_at
        FROM departments d
        JOIN companies c ON d.company_id = c.id
        JOIN users u ON c.user_id = u.id
        ORDER BY d.created_at DESC
    """)
    departments = cursor.fetchall()
    if departments:
        print(f"  {'ID':<5} {'Company':<25} {'Department':<25} {'Created At':<20}")
        print("  " + "-" * 80)
        for d in departments:
            print(f"  {d[0]:<5} {d[1]:<25} {d[2]:<25} {str(d[3]):<20}")
    else:
        print("  Нет департаментов")
    
    # 4. Работники
    print("\n[4] РАБОТНИКИ:")
    cursor.execute("""
        SELECT w.id, d.name as dept_name, w.name, w.surname, w.salary, w.wallet_address, w.is_active
        FROM workers w
        JOIN departments d ON w.department_id = d.id
        ORDER BY w.created_at DESC
    """)
    workers = cursor.fetchall()
    if workers:
        print(f"  {'ID':<5} {'Dept':<20} {'Name':<15} {'Surname':<15} {'Salary':<12} {'Active':<8}")
        print("  " + "-" * 100)
        for w in workers:
            print(f"  {w[0]:<5} {w[1]:<20} {w[2]:<15} {w[3]:<15} {w[4]:<12} {'Yes' if w[6] else 'No':<8}")
    else:
        print("  Нет работников")
    
    # 5. Расходы
    print("\n[5] РАСХОДЫ:")
    cursor.execute("""
        SELECT s.id, u.company_name, COALESCE(d.name, 'CEO') as dept, s.name, s.amount, s.created_at
        FROM additional_spendings s
        JOIN companies c ON s.company_id = c.id
        JOIN users u ON c.user_id = u.id
        LEFT JOIN departments d ON s.department_id = d.id
        ORDER BY s.created_at DESC
    """)
    spendings = cursor.fetchall()
    if spendings:
        print(f"  {'ID':<5} {'Company':<20} {'Dept':<15} {'Name':<20} {'Amount':<12} {'Created':<20}")
        print("  " + "-" * 100)
        for s in spendings:
            print(f"  {s[0]:<5} {s[1]:<20} {s[2]:<15} {s[3]:<20} {s[4]:<12} {str(s[5]):<20}")
    else:
        print("  Нет расходов")
    
    # 6. Доходы
    print("\n[6] ДОХОДЫ:")
    cursor.execute("""
        SELECT r.id, u.company_name, r.amount, r.month, r.year, r.created_at
        FROM revenues r
        JOIN companies c ON r.company_id = c.id
        JOIN users u ON c.user_id = u.id
        ORDER BY r.year DESC, r.month DESC
    """)
    revenues = cursor.fetchall()
    if revenues:
        print(f"  {'ID':<5} {'Company':<20} {'Amount':<12} {'Month':<6} {'Year':<6} {'Created':<20}")
        print("  " + "-" * 80)
        for r in revenues:
            print(f"  {r[0]:<5} {r[1]:<20} {r[2]:<12} {r[3]:<6} {r[4]:<6} {str(r[5]):<20}")
    else:
        print("  Нет доходов")
    
    # 7. Статистика
    print("\n[7] СТАТИСТИКА:")
    cursor.execute("""
        SELECT 
            'users' as table_name, COUNT(*)::text as count FROM users
        UNION ALL
        SELECT 'companies', COUNT(*)::text FROM companies
        UNION ALL
        SELECT 'departments', COUNT(*)::text FROM departments
        UNION ALL
        SELECT 'workers', COUNT(*)::text FROM workers
        UNION ALL
        SELECT 'spendings', COUNT(*)::text FROM additional_spendings
        UNION ALL
        SELECT 'revenues', COUNT(*)::text FROM revenues
        UNION ALL
        SELECT 'payroll_transactions', COUNT(*)::text FROM payroll_transactions
        UNION ALL
        SELECT 'spending_transactions', COUNT(*)::text FROM spending_transactions
    """)
    stats = cursor.fetchall()
    print(f"  {'Table':<25} {'Count':<10}")
    print("  " + "-" * 40)
    for s in stats:
        print(f"  {s[0]:<25} {s[1]:<10}")
    
    conn.close()
    print("\n[OK] Готово!")
    
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")
    exit(1)

