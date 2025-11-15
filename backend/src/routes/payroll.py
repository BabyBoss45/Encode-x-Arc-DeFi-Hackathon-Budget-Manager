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
    """Execute payroll for all active workers in the specified period"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.master_wallet_address:
        raise HTTPException(status_code=400, detail="Master wallet not set")
    
    # Get all active workers
    workers = db.query(Worker).join(Department).filter(
        Department.company_id == company.id,
        Worker.is_active == True
    ).all()
    
    if not workers:
        raise HTTPException(status_code=400, detail="No active workers found")
    
    transactions = []
    
    # Create payroll transactions and execute payments
    for worker in workers:
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
            # Execute payment via Circle API
            # Note: You'll need to store Circle wallet ID for the master wallet
            # For now, this is a placeholder - you'll need to implement wallet ID storage
            result = circle_api.transfer(
                source_wallet_id=company.master_wallet_address,  # This should be Circle wallet ID
                destination_address=worker.wallet_address,
                amount=str(worker.salary),
                token_id="USDC"
            )
            
            payroll_transaction.status = "completed"
            payroll_transaction.transaction_hash = result.get("id")  # Adjust based on Circle API response
            
        except Exception as e:
            payroll_transaction.status = "failed"
            # Log error but continue with other workers
        
        transactions.append(payroll_transaction)
    
    db.commit()
    
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

