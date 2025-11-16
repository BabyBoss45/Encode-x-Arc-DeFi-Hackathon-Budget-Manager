#!/usr/bin/env python3
"""
Check and fix circle_wallet_id column length in PostgreSQL database
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
print("CHECKING AND FIXING circle_wallet_id COLUMN LENGTH")
print("=" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check current column definition
    print("\n[1] Checking current column definition...")
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'companies' AND column_name = 'circle_wallet_id'
    """)
    result = cursor.fetchone()
    if result:
        col_name, data_type, max_length = result
        print(f"  Column: {col_name}")
        print(f"  Type: {data_type}")
        print(f"  Max Length: {max_length if max_length else 'unlimited'}")
        
        if max_length and max_length < 36:
            print(f"\n[WARNING] Column length ({max_length}) is less than UUID length (36)!")
            print("[2] Fixing column length...")
            
            # Update column to VARCHAR(36)
            cursor.execute("ALTER TABLE companies ALTER COLUMN circle_wallet_id TYPE VARCHAR(36)")
            print("  [OK] Updated circle_wallet_id to VARCHAR(36)")
        else:
            print("  [OK] Column length is sufficient")
    else:
        print("  [WARNING] Column not found!")
    
    # Check circle_wallet_set_id
    print("\n[3] Checking circle_wallet_set_id...")
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'companies' AND column_name = 'circle_wallet_set_id'
    """)
    result = cursor.fetchone()
    if result:
        col_name, data_type, max_length = result
        print(f"  Column: {col_name}")
        print(f"  Type: {data_type}")
        print(f"  Max Length: {max_length if max_length else 'unlimited'}")
        
        if max_length and max_length < 36:
            print(f"\n[WARNING] Column length ({max_length}) is less than UUID length (36)!")
            print("[4] Fixing column length...")
            cursor.execute("ALTER TABLE companies ALTER COLUMN circle_wallet_set_id TYPE VARCHAR(36)")
            print("  [OK] Updated circle_wallet_set_id to VARCHAR(36)")
    
    # Check current data
    print("\n[5] Checking current data...")
    cursor.execute("SELECT id, circle_wallet_id, LENGTH(circle_wallet_id) as len FROM companies WHERE circle_wallet_id IS NOT NULL")
    rows = cursor.fetchall()
    if rows:
        print(f"  Found {len(rows)} companies with circle_wallet_id:")
        for row in rows:
            company_id, wallet_id, length = row
            print(f"    Company {company_id}: '{wallet_id}' (length: {length})")
            if length < 36:
                print(f"      [WARNING] Value is truncated! Expected 36, got {length}")
    else:
        print("  No companies with circle_wallet_id found")
    
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    if conn:
        conn.close()

