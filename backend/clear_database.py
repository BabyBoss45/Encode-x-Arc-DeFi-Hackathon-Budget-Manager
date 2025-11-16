"""
Python script for clearing the database
Uses SQLAlchemy for safe clearing of all tables
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from src.database import SessionLocal, Base, engine
from src.models import (
    User, Company, Department, Worker, 
    Revenue, AdditionalSpending, PayrollTransaction, SpendingTransaction
)

# Load .env
load_dotenv(Path(__file__).parent / ".env")

def clear_database():
    """Clear all data from the database"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("CLEARING DATABASE")
        print("=" * 80)
        
        # Count records before clearing
        print("\nRecords before clearing:")
        print(f"  Users: {db.query(User).count()}")
        print(f"  Companies: {db.query(Company).count()}")
        print(f"  Departments: {db.query(Department).count()}")
        print(f"  Workers: {db.query(Worker).count()}")
        print(f"  Revenues: {db.query(Revenue).count()}")
        print(f"  Additional Spendings: {db.query(AdditionalSpending).count()}")
        print(f"  Payroll Transactions: {db.query(PayrollTransaction).count()}")
        print(f"  Spending Transactions: {db.query(SpendingTransaction).count()}")
        
        print("\nClearing tables...")
        
        # Delete in correct order (child tables first)
        db.query(PayrollTransaction).delete()
        print("  [OK] Payroll transactions cleared")
        
        db.query(SpendingTransaction).delete()
        print("  [OK] Spending transactions cleared")
        
        db.query(AdditionalSpending).delete()
        print("  [OK] Additional spendings cleared")
        
        db.query(Revenue).delete()
        print("  [OK] Revenues cleared")
        
        db.query(Worker).delete()
        print("  [OK] Workers cleared")
        
        db.query(Department).delete()
        print("  [OK] Departments cleared")
        
        db.query(Company).delete()
        print("  [OK] Companies cleared")
        
        db.query(User).delete()
        print("  [OK] Users cleared")
        
        # Save changes
        db.commit()
        
        # Count records after clearing
        print("\nRecords after clearing:")
        print(f"  Users: {db.query(User).count()}")
        print(f"  Companies: {db.query(Company).count()}")
        print(f"  Departments: {db.query(Department).count()}")
        print(f"  Workers: {db.query(Worker).count()}")
        print(f"  Revenues: {db.query(Revenue).count()}")
        print(f"  Additional Spendings: {db.query(AdditionalSpending).count()}")
        print(f"  Payroll Transactions: {db.query(PayrollTransaction).count()}")
        print(f"  Spending Transactions: {db.query(SpendingTransaction).count()}")
        
        print("\n" + "=" * 80)
        print("[SUCCESS] DATABASE CLEARED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    import sys
    
    # Confirmation
    print("WARNING: This will delete ALL data from the database!")
    response = input("Are you sure? Type 'yes' to continue: ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    success = clear_database()
    sys.exit(0 if success else 1)

