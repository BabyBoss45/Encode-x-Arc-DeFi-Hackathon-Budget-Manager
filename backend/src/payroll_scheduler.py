"""
Payroll Scheduler: Automatic payroll execution based on company settings
"""
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from src.models import Company, Worker, Department, PayrollTransaction
import os
import subprocess
import sys
from pathlib import Path


def should_run_payroll(company: Company) -> bool:
    """
    Check if payroll should run now based on company.payroll_date and payroll_time.
    
    Returns:
        True if current date/time matches payroll schedule
    """
    if not company.payroll_date or not company.payroll_time:
        return False
    
    now = datetime.now()
    current_date = now.date()
    current_time = now.time().replace(second=0, microsecond=0)
    
    # Check if today is the payroll date
    if current_date != company.payroll_date:
        return False
    
    # Parse payroll time
    try:
        time_parts = company.payroll_time.split(":")
        payroll_hour = int(time_parts[0])
        payroll_minute = int(time_parts[1])
        payroll_time_obj = time(payroll_hour, payroll_minute)
    except (ValueError, IndexError):
        return False
    
    # Check if current time matches payroll time (within the same minute)
    if current_time.hour == payroll_time_obj.hour and current_time.minute == payroll_time_obj.minute:
        return True
    
    return False


def has_payroll_been_run_today(company: Company, db: Session, period_start: date, period_end: date) -> bool:
    """
    Check if payroll has already been executed today for the given period.
    
    Returns:
        True if payroll transactions exist for today with the same period
    """
    today = date.today()
    
    existing = db.query(PayrollTransaction).filter(
        PayrollTransaction.company_id == company.id,
        PayrollTransaction.period_start == period_start,
        PayrollTransaction.period_end == period_end,
        PayrollTransaction.created_at >= datetime.combine(today, datetime.min.time())
    ).first()
    
    return existing is not None


def execute_scheduled_payroll(company: Company, db: Session) -> dict:
    """
    Execute payroll for a company based on scheduled time.
    This function is called by the background scheduler.
    
    Uses company wallet ID (company.circle_wallet_id) as sender
    Uses worker's wallet address (worker.wallet_address) as receiver
    
    Returns:
        Dict with execution results
    """
    print("\n" + "=" * 80)
    print("[PAYROLL SCHEDULER] execute_scheduled_payroll() called")
    print(f"[PAYROLL SCHEDULER] Company ID: {company.id}")
    print(f"[PAYROLL SCHEDULER] Wallet ID: {company.circle_wallet_id}")
    print("=" * 80)
    
    if not should_run_payroll(company):
        print("[PAYROLL SCHEDULER] Not scheduled time - skipping")
        return {"executed": False, "reason": "Not scheduled time"}
    
    # Check if already executed today
    # Calculate period (typically monthly, but can be customized)
    today = date.today()
    period_start = date(today.year, today.month, 1)  # First day of current month
    period_end = today  # Today
    
    print(f"[PAYROLL SCHEDULER] Period: {period_start} to {period_end}")
    
    if has_payroll_been_run_today(company, db, period_start, period_end):
        print("[PAYROLL SCHEDULER] Already executed today - skipping")
        return {"executed": False, "reason": "Already executed today"}
    
    # Get entity secret
    entity_secret_hex = os.getenv("ENTITY_SECRET", "").strip()
    if not entity_secret_hex:
        print("[PAYROLL SCHEDULER] Entity secret not configured")
        return {"executed": False, "reason": "Entity secret not configured"}
    print("[PAYROLL SCHEDULER] Entity secret found")
    
    if not company.circle_wallet_id:
        print("[PAYROLL SCHEDULER] Wallet ID not configured")
        return {"executed": False, "reason": "Circle wallet not configured"}
    
    # Get active workers
    workers = db.query(Worker).join(Department).filter(
        Department.company_id == company.id,
        Worker.is_active == True
    ).all()
    
    print(f"[PAYROLL SCHEDULER] Found {len(workers)} active worker(s)")
    
    if not workers:
        print("[PAYROLL SCHEDULER] No active workers")
        return {"executed": False, "reason": "No active workers"}
    
    # List workers
    for idx, worker in enumerate(workers, 1):
        print(f"[PAYROLL SCHEDULER] Worker {idx}: {worker.name} {worker.surname}")
        print(f"[PAYROLL SCHEDULER]   - Salary: {worker.salary} USDC")
        print(f"[PAYROLL SCHEDULER]   - Wallet Address (Receiver): {worker.wallet_address}")
    
    # Execute payroll for each worker by calling send_transaction_simple.py
    print(f"\n[PAYROLL SCHEDULER] Starting payroll execution...")
    print(f"[PAYROLL SCHEDULER] Calling send_transaction_simple.py for each worker")
    transactions = []
    
    # Get script path
    script_dir = Path(__file__).parent.parent
    script_path = script_dir / "send_transaction_simple.py"
    
    if not script_path.exists():
        print(f"[PAYROLL SCHEDULER] ERROR: Script not found at {script_path}")
        return {"executed": False, "reason": f"Script not found: {script_path}"}
    
    for idx, worker in enumerate(workers, 1):
        print(f"\n[PAYROLL SCHEDULER] Processing worker {idx}/{len(workers)}: {worker.name} {worker.surname}")
        
        payroll_transaction = PayrollTransaction(
            company_id=company.id,
            worker_id=worker.id,
            amount=worker.salary,
            period_start=period_start,
            period_end=period_end,
            status="pending"
        )
        db.add(payroll_transaction)
        db.flush()
        
        try:
            print(f"[PAYROLL SCHEDULER] Calling send_transaction_simple.py...")
            print(f"[PAYROLL SCHEDULER]   Sender (Wallet ID): {company.circle_wallet_id}")
            print(f"[PAYROLL SCHEDULER]   Receiver (Worker Address): {worker.wallet_address}")
            print(f"[PAYROLL SCHEDULER]   Amount: {worker.salary} USDC")
            
            # Call script with parameters: ENTITY_SECRET SENDER_WALLET_ID RECEIVER_ADDRESS AMOUNT
            result = subprocess.run(
                [
                    sys.executable, 
                    str(script_path), 
                    entity_secret_hex,
                    company.circle_wallet_id,
                    worker.wallet_address,
                    str(worker.salary)
                ],
                capture_output=True,
                text=True,
                cwd=str(script_dir),
                timeout=60
            )
            
            print(f"[PAYROLL SCHEDULER] Script output:")
            print(result.stdout)
            if result.stderr:
                print(f"[PAYROLL SCHEDULER] Script errors:")
                print(result.stderr)
            
            if result.returncode == 0:
                # Parse output to get transaction ID if possible
                # Look for "Transaction ID:" in output
                transaction_id = None
                status = "INITIATED"
                
                for line in result.stdout.split('\n'):
                    if 'Transaction ID:' in line:
                        try:
                            transaction_id = line.split('Transaction ID:')[1].strip()
                        except:
                            pass
                    if 'State:' in line:
                        try:
                            status = line.split('State:')[1].strip()
                        except:
                            pass
                
                print(f"[PAYROLL SCHEDULER] Transaction script executed successfully!")
                if transaction_id:
                    payroll_transaction.circle_transaction_id = transaction_id
                    payroll_transaction.status = status
                    print(f"[PAYROLL SCHEDULER]   Transaction ID: {transaction_id}")
                    print(f"[PAYROLL SCHEDULER]   State: {status}")
                else:
                    payroll_transaction.status = "INITIATED"
                
                transactions.append({
                    "worker_id": worker.id,
                    "worker_name": f"{worker.name} {worker.surname}",
                    "amount": worker.salary,
                    "status": payroll_transaction.status,
                    "transaction_id": transaction_id
                })
            else:
                print(f"[PAYROLL SCHEDULER] Script failed with return code {result.returncode}")
                payroll_transaction.status = "failed"
                transactions.append({
                    "worker_id": worker.id,
                    "worker_name": f"{worker.name} {worker.surname}",
                    "amount": worker.salary,
                    "status": "failed",
                    "error": f"Script returned {result.returncode}"
                })
                
        except subprocess.TimeoutExpired:
            print(f"[PAYROLL SCHEDULER] ERROR: Script timeout for worker {worker.id}")
            payroll_transaction.status = "failed"
            transactions.append({
                "worker_id": worker.id,
                "worker_name": f"{worker.name} {worker.surname}",
                "amount": worker.salary,
                "status": "failed",
                "error": "Script timeout"
            })
        except Exception as e:
            print(f"[PAYROLL SCHEDULER] ERROR processing worker {worker.id}: {e}")
            import traceback
            traceback.print_exc()
            payroll_transaction.status = "failed"
            transactions.append({
                "worker_id": worker.id,
                "worker_name": f"{worker.name} {worker.surname}",
                "amount": worker.salary,
                "status": "failed",
                "error": str(e)
            })
    
    db.commit()
    print(f"\n[PAYROLL SCHEDULER] All transactions committed to database")
    print(f"[PAYROLL SCHEDULER] Total processed: {len(transactions)} worker(s)")
    print(f"[PAYROLL SCHEDULER] Total amount: {sum(w.salary for w in workers)} USDC")
    print("=" * 80 + "\n")
    
    return {
        "executed": True,
        "transactions": transactions,
        "total_workers": len(workers),
        "total_amount": sum(w.salary for w in workers)
    }


def check_and_execute_payrolls(db: Session):
    """
    Check all companies and execute payrolls for those scheduled now.
    Called periodically by background scheduler.
    """
    print("\n" + "=" * 80)
    print("[PAYROLL SCHEDULER] ===== CHECKING ALL COMPANIES FOR PAYROLL =====")
    print("=" * 80)
    
    # Get ALL companies first to see total count
    all_companies = db.query(Company).all()
    print(f"[PAYROLL SCHEDULER] Total companies in database: {len(all_companies)}")
    
    # Filter companies with payroll configuration
    companies = db.query(Company).filter(
        Company.payroll_date.isnot(None),
        Company.payroll_time.isnot(None),
        Company.circle_wallet_id.isnot(None)
    ).all()
    
    print(f"[PAYROLL SCHEDULER] Companies with payroll configuration: {len(companies)}")
    
    # Log all companies for debugging
    if len(companies) == 0:
        print("[PAYROLL SCHEDULER] ⚠ No companies found with payroll configuration!")
        print("[PAYROLL SCHEDULER] Companies need:")
        print("[PAYROLL SCHEDULER]   - payroll_date set")
        print("[PAYROLL SCHEDULER]   - payroll_time set")
        print("[PAYROLL SCHEDULER]   - circle_wallet_id set")
    else:
        print(f"\n[PAYROLL SCHEDULER] Processing {len(companies)} company/companies:")
        for idx, company in enumerate(companies, 1):
            print(f"[PAYROLL SCHEDULER]   {idx}. Company ID: {company.id}")
            print(f"[PAYROLL SCHEDULER]      - Payroll Date: {company.payroll_date}")
            print(f"[PAYROLL SCHEDULER]      - Payroll Time: {company.payroll_time}")
            print(f"[PAYROLL SCHEDULER]      - Wallet ID: {company.circle_wallet_id}")
    
    results = []
    for idx, company in enumerate(companies, 1):
        print(f"\n[PAYROLL SCHEDULER] {'='*76}")
        print(f"[PAYROLL SCHEDULER] Processing company {idx}/{len(companies)}: Company ID {company.id}")
        print(f"[PAYROLL SCHEDULER] {'='*76}")
        print(f"[PAYROLL SCHEDULER]   Payroll Date: {company.payroll_date}")
        print(f"[PAYROLL SCHEDULER]   Payroll Time: {company.payroll_time}")
        print(f"[PAYROLL SCHEDULER]   Wallet ID: {company.circle_wallet_id}")
        
        try:
            result = execute_scheduled_payroll(company, db)
            if result.get("executed"):
                print(f"[PAYROLL SCHEDULER] ✓ Payroll executed successfully for company {company.id}")
                results.append({
                    "company_id": company.id,
                    "success": True,
                    "transactions": result.get("transactions", []),
                    "total_amount": result.get("total_amount", 0)
                })
            else:
                # Log reason for not executing
                reason = result.get('reason', 'Unknown')
                print(f"[PAYROLL SCHEDULER] ⚠ Payroll not executed for company {company.id}: {reason}")
                results.append({
                    "company_id": company.id,
                    "success": False,
                    "reason": reason
                })
        except Exception as e:
            print(f"[PAYROLL SCHEDULER] ✗ ERROR executing payroll for company {company.id}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "company_id": company.id,
                "success": False,
                "error": str(e)
            })
    
    print(f"\n[PAYROLL SCHEDULER] {'='*76}")
    print(f"[PAYROLL SCHEDULER] CHECK COMPLETE")
    print(f"[PAYROLL SCHEDULER] Total companies checked: {len(companies)}")
    print(f"[PAYROLL SCHEDULER] Companies processed: {len(results)}")
    print(f"[PAYROLL SCHEDULER] Successful executions: {sum(1 for r in results if r.get('success'))}")
    print(f"[PAYROLL SCHEDULER] Failed/Skipped: {sum(1 for r in results if not r.get('success'))}")
    print(f"[PAYROLL SCHEDULER] {'='*76}\n")
    
    return results

