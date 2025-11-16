#!/usr/bin/env python3
"""
Apply Circle API migration to PostgreSQL database
Adds new columns for Circle wallet integration
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
    print("[ERROR] DATABASE_URL not configured for PostgreSQL!")
    exit(1)

print("=" * 80)
print("APPLYING CIRCLE API MIGRATION")
print("=" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("\n[1] Adding columns to companies table...")
    
    # Add new columns to companies table
    migrations = [
        ("ALTER TABLE companies ADD COLUMN IF NOT EXISTS circle_wallet_id VARCHAR", "circle_wallet_id"),
        ("ALTER TABLE companies ADD COLUMN IF NOT EXISTS circle_wallet_set_id VARCHAR", "circle_wallet_set_id"),
        ("ALTER TABLE companies ADD COLUMN IF NOT EXISTS entity_secret_encrypted TEXT", "entity_secret_encrypted"),
    ]
    
    for sql, column_name in migrations:
        try:
            cursor.execute(sql)
            print(f"  [OK] Added column: {column_name}")
        except Exception as e:
            print(f"  [WARNING] {column_name}: {e}")
    
    print("\n[2] Adding column to payroll_transactions table...")
    
    # Add circle_transaction_id to payroll_transactions
    try:
        cursor.execute("ALTER TABLE payroll_transactions ADD COLUMN IF NOT EXISTS circle_transaction_id VARCHAR")
        print("  [OK] Added column: circle_transaction_id")
    except Exception as e:
        print(f"  [WARNING] circle_transaction_id: {e}")
    
    print("\n[3] Creating indexes...")
    
    # Create indexes
    indexes = [
        ("CREATE INDEX IF NOT EXISTS idx_payroll_transactions_circle_tx_id ON payroll_transactions(circle_transaction_id)", "payroll_transactions.circle_transaction_id"),
        ("CREATE INDEX IF NOT EXISTS idx_companies_circle_wallet_id ON companies(circle_wallet_id)", "companies.circle_wallet_id"),
    ]
    
    for sql, index_name in indexes:
        try:
            cursor.execute(sql)
            print(f"  [OK] Created index: {index_name}")
        except Exception as e:
            print(f"  [WARNING] {index_name}: {e}")
    
    print("\n[4] Verifying migration...")
    
    # Verify columns exist
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'companies' 
        AND column_name IN ('circle_wallet_id', 'circle_wallet_set_id', 'entity_secret_encrypted')
        ORDER BY column_name
    """)
    company_columns = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'payroll_transactions' 
        AND column_name = 'circle_transaction_id'
    """)
    payroll_columns = [row[0] for row in cursor.fetchall()]
    
    print(f"\n  Companies columns: {', '.join(company_columns) if company_columns else 'None found'}")
    print(f"  Payroll columns: {', '.join(payroll_columns) if payroll_columns else 'None found'}")
    
    if len(company_columns) == 3 and len(payroll_columns) == 1:
        print("\n" + "=" * 80)
        print("[OK] Migration completed successfully!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("[WARNING] Some columns may be missing. Check output above.")
        print("=" * 80)
    
    conn.close()
    
except Exception as e:
    print(f"\n[ERROR] Migration failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

