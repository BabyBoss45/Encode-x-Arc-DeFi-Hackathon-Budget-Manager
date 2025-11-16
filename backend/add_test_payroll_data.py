"""
Скрипт для добавления тестовых данных для автоматической отправки зарплаты
"""
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from src.database import SessionLocal
from src.models import User, Company, Department, Worker
from src.auth import get_password_hash

# Load .env
load_dotenv(Path(__file__).parent / ".env")

# Test data
CEO_WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
DEPARTMENT_NAME = "finance"
WORKER_WALLET_ADDRESS = "0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb"
WORKER_SALARY = 10.0  # USDC

def add_test_data():
    """Добавить тестовые данные в БД"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("ADDING TEST DATA FOR AUTOMATIC PAYROLL")
        print("=" * 80)
        
        # Calculate time 2 minutes from now
        now = datetime.now()
        payroll_datetime = now + timedelta(minutes=2)
        payroll_date = payroll_datetime.date()
        payroll_time = payroll_datetime.strftime("%H:%M")
        
        print(f"\nCurrent time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Payroll scheduled for: {payroll_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Payroll Date: {payroll_date}")
        print(f"Payroll Time: {payroll_time}")
        print()
        
        # 1. Create or find user
        print("1. Checking user...")
        user_email = "test@example.com"
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            print(f"   Creating new user: {user_email}")
            user = User(
                email=user_email,
                password_hash=get_password_hash("test123"),
                company_name="Test Company"
            )
            db.add(user)
            db.flush()
            print(f"   [OK] User created (ID: {user.id})")
        else:
            print(f"   [OK] User found (ID: {user.id})")
        
        # 2. Create or update company
        print("\n2. Checking company...")
        company = db.query(Company).filter(Company.user_id == user.id).first()
        
        if not company:
            print("   Creating new company...")
            company = Company(
                user_id=user.id,
                circle_wallet_id=CEO_WALLET_ID,
                payroll_date=payroll_date,
                payroll_time=payroll_time
            )
            db.add(company)
            db.flush()
            print(f"   [OK] Company created (ID: {company.id})")
        else:
            print(f"   Updating existing company (ID: {company.id})...")
            company.circle_wallet_id = CEO_WALLET_ID
            company.payroll_date = payroll_date
            company.payroll_time = payroll_time
            print(f"   [OK] Company updated")
        
        print(f"   - Wallet ID: {company.circle_wallet_id}")
        print(f"   - Payroll Date: {company.payroll_date}")
        print(f"   - Payroll Time: {company.payroll_time}")
        
        # 3. Create department
        print("\n3. Checking department...")
        dept_name = DEPARTMENT_NAME
        department = db.query(Department).filter(
            Department.company_id == company.id,
            Department.name == dept_name
        ).first()
        
        if not department:
            print(f"   Creating department: {dept_name}")
            department = Department(
                company_id=company.id,
                name=dept_name
            )
            db.add(department)
            db.flush()
            print(f"   [OK] Department created (ID: {department.id})")
        else:
            print(f"   [OK] Department found (ID: {department.id})")
        
        # 4. Create or update worker
        print("\n4. Checking worker...")
        worker = db.query(Worker).filter(
            Worker.department_id == department.id,
            Worker.wallet_address == WORKER_WALLET_ADDRESS
        ).first()
        
        if not worker:
            print("   Creating new worker...")
            worker = Worker(
                department_id=department.id,
                name="Finance",
                surname="Worker",
                salary=WORKER_SALARY,
                wallet_address=WORKER_WALLET_ADDRESS,
                is_active=True
            )
            db.add(worker)
            db.flush()
            print(f"   [OK] Worker created (ID: {worker.id})")
        else:
            print(f"   Updating existing worker (ID: {worker.id})...")
            worker.salary = WORKER_SALARY
            worker.is_active = True
            worker.name = "Finance"
            worker.surname = "Worker"
            print(f"   [OK] Worker updated")
        
        print(f"   - Name: {worker.name} {worker.surname}")
        print(f"   - Salary: {worker.salary} USDC")
        print(f"   - Wallet Address: {worker.wallet_address}")
        print(f"   - Active: {worker.is_active}")
        
        # Save changes
        db.commit()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] TEST DATA ADDED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nAutomatic payroll scheduled for:")
        print(f"  Date: {payroll_date}")
        print(f"  Time: {payroll_time}")
        print(f"\nWill send:")
        print(f"  From CEO wallet: {CEO_WALLET_ID}")
        print(f"  To worker wallet: {WORKER_WALLET_ADDRESS}")
        print(f"  Amount: {WORKER_SALARY} USDC")
        print("\nMake sure the server is running for automatic execution!")
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
    success = add_test_data()
    sys.exit(0 if success else 1)

