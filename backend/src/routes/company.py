"""
Company routes: master wallet setup
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Company
from ..schemas import CompanyCreate, CompanyResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("/", response_model=CompanyResponse)
async def get_company(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get company information"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/master-wallet", response_model=CompanyResponse)
async def update_master_wallet(
    wallet_data: CompanyCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update master wallet address, payroll date and time"""
    # Basic wallet validation
    if not wallet_data.master_wallet_address.startswith("0x") or len(wallet_data.master_wallet_address) != 42:
        raise HTTPException(status_code=400, detail="Invalid wallet address format")
    
    # Validate payroll_time format (HH:MM)
    if wallet_data.payroll_time is not None:
        try:
            parts = wallet_data.payroll_time.split(":")
            if len(parts) != 2:
                raise ValueError
            hour = int(parts[0])
            minute = int(parts[1])
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Payroll time must be in HH:MM format (24-hour)")
    
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company.master_wallet_address = wallet_data.master_wallet_address
    company.payroll_date = wallet_data.payroll_date
    company.payroll_time = wallet_data.payroll_time
    db.commit()
    db.refresh(company)
    return company

