"""
Быстрое обновление времени отправки зарплаты
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from src.database import SessionLocal
from src.models import Company
from datetime import date

# Load .env
load_dotenv(Path(__file__).parent / ".env")

def set_payroll_time(target_time: str):
    """Установить время отправки зарплаты"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print(f"SETTING PAYROLL TIME TO {target_time}")
        print("=" * 80)
        
        # Find company with CEO wallet ID
        company = db.query(Company).filter(
            Company.circle_wallet_id == "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
        ).first()
        
        if not company:
            print("[ERROR] Company not found")
            return False
        
        # Validate time format
        try:
            parts = target_time.split(":")
            if len(parts) != 2:
                raise ValueError
            hour = int(parts[0])
            minute = int(parts[1])
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError
        except (ValueError, IndexError):
            print(f"[ERROR] Invalid time format: {target_time}. Use HH:MM format")
            return False
        
        # Update payroll time
        company.payroll_date = date.today()
        company.payroll_time = target_time
        
        db.commit()
        
        print(f"[SUCCESS] Payroll time updated!")
        print(f"  Date: {company.payroll_date}")
        print(f"  Time: {company.payroll_time}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_time = sys.argv[1]
    else:
        target_time = "02:53"  # Default
    
    success = set_payroll_time(target_time)
    sys.exit(0 if success else 1)

