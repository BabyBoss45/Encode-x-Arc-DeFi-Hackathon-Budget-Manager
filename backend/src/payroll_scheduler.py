"""
Payroll Scheduler: Automatic payroll execution based on company settings
"""
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from src.models import Company, Worker, Department, PayrollTransaction
from src.circle_api import circle_api
import os


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
    
    # Check balance
    print(f"\n[PAYROLL SCHEDULER] Checking wallet ID balance...")
    try:
        wallet_balance = circle_api.get_wallet_balance(company.circle_wallet_id)
        total_payroll = sum(w.salary for w in workers)
        print(f"[PAYROLL SCHEDULER] Wallet Balance: {wallet_balance} USDC")
        print(f"[PAYROLL SCHEDULER] Total Payroll Required: {total_payroll} USDC")
        
        if wallet_balance < total_payroll:
            print(f"[PAYROLL SCHEDULER] Insufficient balance!")
            return {
                "executed": False,
                "reason": f"Insufficient balance: {wallet_balance} USDC < {total_payroll} USDC required"
            }
        print(f"[PAYROLL SCHEDULER] Balance sufficient ✓")
    except Exception as e:
        print(f"[PAYROLL SCHEDULER] Balance check failed: {e}")
        return {"executed": False, "reason": f"Balance check failed: {str(e)}"}
    
    # Execute payroll for each worker
    print(f"\n[PAYROLL SCHEDULER] Starting payroll execution...")
    transactions = []
    
    # Try to get USDC token ID (will be auto-detected if not set)
    usdc_token_id = os.getenv("USDC_TOKEN_ID", None)
    if not usdc_token_id or len(usdc_token_id) != 36:
        print("[PAYROLL SCHEDULER] USDC_TOKEN_ID not set or invalid, will auto-detect from wallet")
        usdc_token_id = None  # Let circle_api auto-detect
    
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
            print(f"[PAYROLL SCHEDULER] Calling CircleAPI.transfer_usdc()...")
            print(f"[PAYROLL SCHEDULER]   Sender (Wallet ID): {company.circle_wallet_id}")
            print(f"[PAYROLL SCHEDULER]   Receiver (Worker Address): {worker.wallet_address}")
            print(f"[PAYROLL SCHEDULER]   Amount: {worker.salary} USDC")
            
            result = circle_api.transfer_usdc(
                entity_secret_hex=entity_secret_hex,
                wallet_id=company.circle_wallet_id,  # Company wallet ID (sender)
                destination_address=worker.wallet_address,  # Worker's address (receiver)
                amount=str(worker.salary),
                token_id=usdc_token_id,
                blockchain="ARC-TESTNET"
            )
            
            circle_tx_id = result.get("id")
            circle_state = result.get("state", "INITIATED")
            
            print(f"[PAYROLL SCHEDULER] Transaction created successfully!")
            print(f"[PAYROLL SCHEDULER]   Transaction ID: {circle_tx_id}")
            print(f"[PAYROLL SCHEDULER]   State: {circle_state}")
            
            payroll_transaction.circle_transaction_id = circle_tx_id
            payroll_transaction.status = circle_state
            
            tx_data = result.get("data", {})
            if tx_data.get("txHash"):
                payroll_transaction.transaction_hash = tx_data.get("txHash")
                print(f"[PAYROLL SCHEDULER]   Transaction Hash: {tx_data.get('txHash')}")
            
            transactions.append({
                "worker_id": worker.id,
                "worker_name": f"{worker.name} {worker.surname}",
                "amount": worker.salary,
                "status": circle_state,
                "transaction_id": circle_tx_id
            })
        except Exception as e:
            print(f"[PAYROLL SCHEDULER] ERROR processing worker {worker.id}: {e}")
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
    print("\n[PAYROLL SCHEDULER] check_and_execute_payrolls() called")
    print(f"[PAYROLL SCHEDULER] Checking all companies for scheduled payrolls...")
    
    companies = db.query(Company).filter(
        Company.payroll_date.isnot(None),
        Company.payroll_time.isnot(None),
        Company.circle_wallet_id.isnot(None)
    ).all()
    
    print(f"[PAYROLL SCHEDULER] Found {len(companies)} company/companies with payroll configuration")
    
    results = []
    for company in companies:
        print(f"\n[PAYROLL SCHEDULER] Checking company {company.id}...")
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
        except Exception as e:
            print(f"[PAYROLL SCHEDULER] ✗ ERROR executing payroll for company {company.id}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "company_id": company.id,
                "success": False,
                "error": str(e)
            })
    
    print(f"\n[PAYROLL SCHEDULER] Check complete. Processed {len(results)} company/companies")
    return results

