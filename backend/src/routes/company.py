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
        # Auto-create company if it doesn't exist (shouldn't happen, but handle it)
        company = Company(user_id=current_user.id)
        db.add(company)
        db.commit()
        db.refresh(company)
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
        # Auto-create company if it doesn't exist (shouldn't happen, but handle it)
        company = Company(user_id=current_user.id)
        db.add(company)
        db.commit()
        db.refresh(company)
    
    # Validate wallet address if provided
    if wallet_data.master_wallet_address:
        wallet_addr = wallet_data.master_wallet_address.strip()
        # More flexible validation: allow addresses with or without 0x prefix
        # Ethereum addresses are 42 chars with 0x, or 40 chars without
        if wallet_addr.startswith("0x"):
            if len(wallet_addr) != 42:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid wallet address format: expected 42 characters (got {len(wallet_addr)}). Address: {wallet_addr[:20]}..."
                )
        else:
            # If no 0x prefix, add it and check length
            if len(wallet_addr) == 40:
                wallet_addr = "0x" + wallet_addr
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid wallet address format: expected 40 characters without 0x or 42 with 0x (got {len(wallet_addr)}). Address: {wallet_addr[:20]}..."
                )
        
        # Validate hex characters
        try:
            int(wallet_addr[2:], 16)  # Check if it's valid hex after 0x
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid wallet address format: must contain only hexadecimal characters. Address: {wallet_addr[:20]}..."
            )
        
        company.master_wallet_address = wallet_addr
    
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
        wallet_id_clean = wallet_data.circle_wallet_id.strip()
        
        print(f"[DEBUG] Received circle_wallet_id: '{wallet_id_clean}' (length: {len(wallet_id_clean)})")
        
        if not uuid_pattern.match(wallet_id_clean):
            print(f"[ERROR] Invalid UUID format: '{wallet_id_clean}'")
            raise HTTPException(status_code=400, detail="Invalid Circle wallet ID format (must be UUID)")
        
        # UUID should be exactly 36 characters (32 hex + 4 dashes)
        if len(wallet_id_clean) != 36:
            print(f"[ERROR] UUID length mismatch: expected 36, got {len(wallet_id_clean)}")
            raise HTTPException(status_code=400, detail=f"Invalid Circle wallet ID length: expected 36 characters, got {len(wallet_id_clean)}")
        
        print(f"[DEBUG] Setting company.circle_wallet_id to: '{wallet_id_clean}'")
        company.circle_wallet_id = wallet_id_clean
        print(f"[DEBUG] After assignment, company.circle_wallet_id = '{company.circle_wallet_id}'")
    
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
    
    # Verify the value was saved correctly
    print(f"[DEBUG] After commit, company.circle_wallet_id = '{company.circle_wallet_id}' (length: {len(company.circle_wallet_id) if company.circle_wallet_id else 0})")
    
    # Clear dashboard cache since company settings changed
    from ..cache import clear_cache
    clear_cache(current_user.id)
    
    return company

