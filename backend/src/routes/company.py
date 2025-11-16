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
    """Update master wallet address, Circle wallet ID, entity secret, payroll date and time"""
    from ..circle_api import circle_api
    
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Validate wallet address if provided
    if wallet_data.master_wallet_address:
        if not wallet_data.master_wallet_address.startswith("0x") or len(wallet_data.master_wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        company.master_wallet_address = wallet_data.master_wallet_address
    
    # Validate and encrypt entity secret if provided
    if wallet_data.entity_secret:
        entity_secret = wallet_data.entity_secret.strip()
        # Validate format (64 hex characters)
        if len(entity_secret) != 64:
            raise HTTPException(status_code=400, detail="Entity secret must be 64 hex characters")
        try:
            # Validate it's valid hex
            int(entity_secret, 16)
            # Encrypt entity secret
            try:
                encrypted_secret = circle_api.encrypt_entity_secret(entity_secret)
                company.entity_secret_encrypted = encrypted_secret
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to encrypt entity secret: {str(e)}")
        except ValueError:
            raise HTTPException(status_code=400, detail="Entity secret must be valid hex string")
    
    # Update Circle wallet IDs if provided
    if wallet_data.circle_wallet_id:
        # Validate UUID format
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
        if not uuid_pattern.match(wallet_data.circle_wallet_id):
            raise HTTPException(status_code=400, detail="Invalid Circle wallet ID format (must be UUID)")
        company.circle_wallet_id = wallet_data.circle_wallet_id
    
    if wallet_data.circle_wallet_set_id:
        company.circle_wallet_set_id = wallet_data.circle_wallet_set_id
    
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
            company.payroll_time = wallet_data.payroll_time
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Payroll time must be in HH:MM format (24-hour)")
    
    if wallet_data.payroll_date is not None:
        company.payroll_date = wallet_data.payroll_date
    
    db.commit()
    db.refresh(company)
    
    # Clear dashboard cache since company settings changed
    from ..cache import clear_cache
    clear_cache(current_user.id)
    
    return company

