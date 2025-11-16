"""
Check automatic payroll settings
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from src.database import SessionLocal
from src.models import Company, Department, Worker

# Load .env
load_dotenv(Path(__file__).parent / ".env")

def check_schedule():
    """Check automatic payroll settings"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("CHECKING AUTOMATIC PAYROLL SCHEDULE")
        print("=" * 80)
        
        now = datetime.now()
        print(f"\nCurrent time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Current date: {now.date()}")
        print(f"Current time: {now.time().strftime('%H:%M')}")
        
        # Find company with CEO wallet ID
        company = db.query(Company).filter(
            Company.circle_wallet_id == "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
        ).first()
        
        if not company:
            print("\n[ERROR] Company not found with CEO wallet ID")
            return False
        
        print(f"\nCompany ID: {company.id}")
        print(f"CEO Wallet ID: {company.circle_wallet_id}")
        print(f"Payroll Date: {company.payroll_date}")
        print(f"Payroll Time: {company.payroll_time}")
        
        # Check if scheduled for today
        if company.payroll_date == now.date():
            print(f"\n[OK] Payroll scheduled for TODAY")
        else:
            print(f"\n[WARNING] Payroll date ({company.payroll_date}) is not today")
        
        # Check workers
        departments = db.query(Department).filter(
            Department.company_id == company.id
        ).all()
        
        total_workers = 0
        total_salary = 0.0
        
        for dept in departments:
            workers = db.query(Worker).filter(
                Worker.department_id == dept.id,
                Worker.is_active == True
            ).all()
            
            for worker in workers:
                total_workers += 1
                total_salary += worker.salary
                print(f"\n  Department: {dept.name}")
                print(f"    Worker: {worker.name} {worker.surname}")
                print(f"    Salary: {worker.salary} USDC")
                print(f"    Wallet: {worker.wallet_address}")
        
        print(f"\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total active workers: {total_workers}")
        print(f"Total salary to pay: {total_salary} USDC")
        
        if company.payroll_date and company.payroll_time:
            payroll_datetime = datetime.combine(company.payroll_date, 
                                                datetime.strptime(company.payroll_time, "%H:%M").time())
            time_diff = (payroll_datetime - now).total_seconds()
            
            if time_diff > 0:
                minutes = int(time_diff / 60)
                seconds = int(time_diff % 60)
                print(f"\nPayroll will execute in: {minutes} minutes {seconds} seconds")
                print(f"At: {payroll_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            elif time_diff >= -60:
                print(f"\n[INFO] Payroll time is NOW or within the last minute")
                print(f"Scheduled for: {payroll_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"\n[WARNING] Payroll time has passed")
                print(f"Was scheduled for: {payroll_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check ENTITY_SECRET
        entity_secret = os.getenv("ENTITY_SECRET", "").strip()
        if entity_secret:
            print(f"\n[OK] ENTITY_SECRET is set ({len(entity_secret)} chars)")
        else:
            print(f"\n[ERROR] ENTITY_SECRET is not set in .env")
        
        print("\n" + "=" * 80)
        print("Make sure the server is running for automatic execution!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = check_schedule()
    sys.exit(0 if success else 1)

