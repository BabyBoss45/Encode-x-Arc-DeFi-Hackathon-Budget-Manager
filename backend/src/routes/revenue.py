"""
Revenue routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Revenue, Company
from ..schemas import RevenueCreate, RevenueResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/revenue", tags=["revenue"])


@router.get("/", response_model=List[RevenueResponse])
async def get_revenues(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all revenues for company"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    revenues = db.query(Revenue).filter(Revenue.company_id == company.id).order_by(Revenue.year.desc(), Revenue.month.desc()).all()
    return revenues


@router.post("/", response_model=RevenueResponse)
async def create_revenue(
    revenue_data: RevenueCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create monthly revenue"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Validate month
    if revenue_data.month < 1 or revenue_data.month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    # Check if revenue for this month/year already exists
    existing = db.query(Revenue).filter(
        Revenue.company_id == company.id,
        Revenue.month == revenue_data.month,
        Revenue.year == revenue_data.year
    ).first()
    
    if existing:
        # Update existing revenue
        existing.amount = revenue_data.amount
        db.commit()
        db.refresh(existing)
        return existing
    
    revenue = Revenue(
        company_id=company.id,
        amount=revenue_data.amount,
        month=revenue_data.month,
        year=revenue_data.year
    )
    db.add(revenue)
    db.commit()
    db.refresh(revenue)
    return revenue

