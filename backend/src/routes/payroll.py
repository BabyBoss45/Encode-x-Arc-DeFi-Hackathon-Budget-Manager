"""
Payroll routes: execute payroll payments
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..models import Worker, Company, Department, PayrollTransaction
from ..schemas import PayrollCreate, PayrollTransactionResponse
from ..auth import get_current_user
from ..circle_api import circle_api

router = APIRouter(prefix="/api/payroll", tags=["payroll"])


@router.post("/execute", response_model=List[PayrollTransactionResponse])
async def execute_payroll(
    payroll_data: PayrollCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute payroll for all active workers in the specified period using Circle API.
    
    Uses company wallet ID (company.circle_wallet_id) as sender
    Uses worker's wallet address (worker.wallet_address) as receiver
    """
    import os
    
    print("\n" + "=" * 80)
    print("[PAYROLL API] execute_payroll() called (manual execution)")
    print(f"[PAYROLL API] User ID: {current_user.id}")
    print(f"[PAYROLL API] Period: {payroll_data.period_start} to {payroll_data.period_end}")
    print("=" * 80)
    
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        print("[PAYROLL API] Company not found")
        raise HTTPException(status_code=404, detail="Company not found")
    
    print(f"[PAYROLL API] Company ID: {company.id}")
    print(f"[PAYROLL API] Wallet ID (Sender): {company.circle_wallet_id}")
    
    # Check Circle wallet configuration
    if not company.circle_wallet_id:
        print("[PAYROLL API] Wallet ID not configured")
        raise HTTPException(status_code=400, detail="Circle wallet ID not set. Please configure your Circle wallet in company settings.")
    
    # Get entity secret from environment or company (prefer environment for security)
    entity_secret_hex = os.getenv("ENTITY_SECRET", "").strip()
    if not entity_secret_hex and company.entity_secret_encrypted:
        # If encrypted secret is stored, we need the original to re-encrypt
        # For security, prefer environment variable
        print("[PAYROLL API] Entity secret not found in environment")
        raise HTTPException(
            status_code=400, 
            detail="Entity secret not found. Please set ENTITY_SECRET in environment variables or provide it in company settings."
        )
    
    if not entity_secret_hex or len(entity_secret_hex) != 64:
        print("[PAYROLL API] Invalid entity secret format")
        raise HTTPException(status_code=400, detail="Entity secret must be 64 hex characters")
    
    print("[PAYROLL API] Entity secret found")
    
    # Get all active workers
    workers = db.query(Worker).join(Department).filter(
        Department.company_id == company.id,
        Worker.is_active == True
    ).all()
    
    print(f"[PAYROLL API] Found {len(workers)} active worker(s)")
    
    if not workers:
        print("[PAYROLL API] No active workers found")
        raise HTTPException(status_code=400, detail="No active workers found")
    
    # List workers
    for idx, worker in enumerate(workers, 1):
        print(f"[PAYROLL API] Worker {idx}: {worker.name} {worker.surname}")
        print(f"[PAYROLL API]   - Salary: {worker.salary} USDC")
        print(f"[PAYROLL API]   - Wallet Address (Receiver): {worker.wallet_address}")
    
    # Check wallet balance before processing
    print(f"\n[PAYROLL API] Checking wallet ID balance...")
    try:
        wallet_balance = circle_api.get_wallet_balance(company.circle_wallet_id)
        total_payroll = sum(w.salary for w in workers)
        print(f"[PAYROLL API] Wallet Balance: {wallet_balance} USDC")
        print(f"[PAYROLL API] Total Payroll Required: {total_payroll} USDC")
        
        if wallet_balance < total_payroll:
            print(f"[PAYROLL API] Insufficient balance!")
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient wallet balance. Available: {wallet_balance} USDC, Required: {total_payroll} USDC"
            )
        print(f"[PAYROLL API] Balance sufficient ✓")
    except HTTPException:
        raise
    except Exception as e:
        # Log but don't fail if balance check fails
        print(f"[PAYROLL API] Warning: Could not check wallet balance: {e}")
    
    transactions = []
    
    # USDC Token ID - can be configured or will be auto-detected
    usdc_token_id = os.getenv("USDC_TOKEN_ID", None)
    if usdc_token_id and len(usdc_token_id) == 36:  # Valid UUID length
        print(f"[PAYROLL API] USDC Token ID: {usdc_token_id}")
    else:
        print(f"[PAYROLL API] USDC Token ID: Not provided (will auto-detect from wallet)")
        usdc_token_id = None  # Let circle_api auto-detect
    
    # Create payroll transactions and execute payments
    print(f"\n[PAYROLL API] Starting payroll execution...")
    for idx, worker in enumerate(workers, 1):
        print(f"\n[PAYROLL API] Processing worker {idx}/{len(workers)}: {worker.name} {worker.surname}")
        
        # Create transaction record
        payroll_transaction = PayrollTransaction(
            company_id=company.id,
            worker_id=worker.id,
            amount=worker.salary,
            period_start=payroll_data.period_start,
            period_end=payroll_data.period_end,
            status="pending"
        )
        db.add(payroll_transaction)
        db.flush()  # Get the ID
        
        try:
            print(f"[PAYROLL API] Calling CircleAPI.transfer_usdc()...")
            print(f"[PAYROLL API]   Sender (Wallet ID): {company.circle_wallet_id}")
            print(f"[PAYROLL API]   Receiver (Worker Address): {worker.wallet_address}")
            print(f"[PAYROLL API]   Amount: {worker.salary} USDC")
            
            # Execute payment via Circle API
            result = circle_api.transfer_usdc(
                entity_secret_hex=entity_secret_hex,
                wallet_id=company.circle_wallet_id,  # Company wallet ID (sender)
                destination_address=worker.wallet_address,  # Worker's address (receiver)
                amount=str(worker.salary),
                token_id=usdc_token_id,
                blockchain="ARC-TESTNET"
            )
            
            # Update transaction with Circle response
            circle_tx_id = result.get("id")
            circle_state = result.get("state", "INITIATED")
            
            print(f"[PAYROLL API] Transaction created successfully!")
            print(f"[PAYROLL API]   Transaction ID: {circle_tx_id}")
            print(f"[PAYROLL API]   State: {circle_state}")
            
            payroll_transaction.circle_transaction_id = circle_tx_id
            payroll_transaction.status = circle_state  # INITIATED, QUEUED, SENT, CONFIRMED, COMPLETE
            
            # Get transaction hash if available (may be None initially)
            tx_data = result.get("data", {})
            if tx_data.get("txHash"):
                payroll_transaction.transaction_hash = tx_data.get("txHash")
                print(f"[PAYROLL API]   Transaction Hash: {tx_data.get('txHash')}")
            
        except Exception as e:
            payroll_transaction.status = "failed"
            print(f"[PAYROLL API] ERROR processing worker {worker.id}: {e}")
            # Log error but continue with other workers
        
        transactions.append(payroll_transaction)
    
    db.commit()
    print(f"\n[PAYROLL API] All transactions committed to database")
    print(f"[PAYROLL API] Total processed: {len(transactions)} worker(s)")
    print("=" * 80 + "\n")
    
    # Clear dashboard cache since transactions changed
    from ..cache import clear_cache
    clear_cache(current_user.id)
    
    # Refresh all transactions
    for txn in transactions:
        db.refresh(txn)
    
    return transactions


@router.get("/transactions", response_model=List[PayrollTransactionResponse])
async def get_payroll_transactions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payroll transactions"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    transactions = db.query(PayrollTransaction).filter(
        PayrollTransaction.company_id == company.id
    ).order_by(PayrollTransaction.created_at.desc()).all()
    
    return transactions

