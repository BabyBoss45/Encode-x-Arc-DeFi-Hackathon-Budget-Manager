"""
Additional spending routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import AdditionalSpending, Company, Department
from ..schemas import SpendingCreate, SpendingResponse
from pydantic import BaseModel
from ..auth import get_current_user
from ..cache import clear_cache

router = APIRouter(prefix="/api/spendings", tags=["spendings"])


@router.get("/", response_model=List[SpendingResponse])
async def get_spendings(
    department_id: int = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all spendings, optionally filtered by department"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    query = db.query(AdditionalSpending).filter(AdditionalSpending.company_id == company.id)
    
    if department_id:
        query = query.filter(AdditionalSpending.department_id == department_id)
    else:
        # If no department_id, show CEO-level spendings (department_id is None)
        query = query.filter(AdditionalSpending.department_id.is_(None))
    
    spendings = query.all()
    return spendings


@router.post("/", response_model=SpendingResponse)
async def create_spending(
    spending_data: SpendingCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create additional spending"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # If department_id is provided, verify it belongs to company
    if spending_data.department_id:
        department = db.query(Department).filter(
            Department.id == spending_data.department_id,
            Department.company_id == company.id
        ).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
    
    # Validate wallet address
    if not spending_data.wallet_address.startswith("0x") or len(spending_data.wallet_address) != 42:
        raise HTTPException(status_code=400, detail="Invalid wallet address format")
    
    spending = AdditionalSpending(
        company_id=company.id,
        department_id=spending_data.department_id,
        name=spending_data.name,
        amount=spending_data.amount,
        wallet_address=spending_data.wallet_address
    )
    db.add(spending)
    db.commit()
    db.refresh(spending)
    
    # Clear dashboard cache since stats changed
    clear_cache(current_user.id)
    
    return spending


@router.delete("/{spending_id}")
async def delete_spending(
    spending_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a spending"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    spending = db.query(AdditionalSpending).filter(
        AdditionalSpending.id == spending_id,
        AdditionalSpending.company_id == company.id
    ).first()
    
    if not spending:
        raise HTTPException(status_code=404, detail="Spending not found")
    
    db.delete(spending)
    db.commit()
    
    # Clear dashboard cache since stats changed
    clear_cache(current_user.id)
    
    return {"message": "Spending deleted"}


class DateUpdate(BaseModel):
    date: str

@router.patch("/{spending_id}/date", response_model=SpendingResponse)
async def update_spending_date(
    spending_id: int,
    date_data: DateUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update spending date (created_at)"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    spending = db.query(AdditionalSpending).filter(
        AdditionalSpending.id == spending_id,
        AdditionalSpending.company_id == company.id
    ).first()
    
    if not spending:
        raise HTTPException(status_code=404, detail="Spending not found")
    
    # Update created_at with the new date
    from datetime import datetime, date as date_type
    try:
        # Parse date string (format: YYYY-MM-DD)
        date_str = date_data.date
        if "T" in date_str:
            date_str = date_str.split("T")[0]
        
        # Parse YYYY-MM-DD format
        date_parts = date_str.split("-")
        if len(date_parts) == 3:
            year, month, day = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
            date_obj = date_type(year, month, day)
            # Convert to datetime for created_at field
            new_date = datetime.combine(date_obj, datetime.min.time())
        else:
            new_date = datetime.fromisoformat(date_str)
        
        spending.created_at = new_date
        db.commit()
        db.refresh(spending)
        return spending
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

