"""
Circle API routes: Get information from Circle API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from ..database import get_db
from ..models import Company
from ..auth import get_current_user
from ..circle_api import circle_api
from pydantic import BaseModel

router = APIRouter(prefix="/api/circle", tags=["circle"])


# Response schemas
class WalletBalanceResponse(BaseModel):
    wallet_id: str
    balance: float
    currency: str = "USDC"


class WalletInfoResponse(BaseModel):
    wallet_id: str
    address: Optional[str] = None
    state: Optional[str] = None
    wallet_set_id: Optional[str] = None


class TransactionStatusResponse(BaseModel):
    transaction_id: str
    state: str
    tx_hash: Optional[str] = None
    data: Optional[Dict] = None


class TokenBalance(BaseModel):
    token_id: Optional[str] = None
    token_address: Optional[str] = None
    symbol: str
    amount: str
    decimals: Optional[int] = None


class WalletBalancesResponse(BaseModel):
    wallet_id: str
    balances: List[TokenBalance]


@router.get("/wallet/balance", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wallet ID USDC balance from Circle API
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.circle_wallet_id:
        raise HTTPException(
            status_code=400, 
            detail="Circle wallet ID not configured. Please set it in company settings."
        )
    
    try:
        balance = circle_api.get_wallet_balance(company.circle_wallet_id)
        return WalletBalanceResponse(
            wallet_id=company.circle_wallet_id,
            balance=balance,
            currency="USDC"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wallet balance: {str(e)}"
        )


@router.get("/wallet/info", response_model=WalletInfoResponse)
async def get_wallet_info(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get wallet ID information (address, state) from Circle API
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.circle_wallet_id:
        raise HTTPException(
            status_code=400, 
            detail="Circle wallet ID not configured. Please set it in company settings."
        )
    
    try:
        address = circle_api.get_wallet_address(company.circle_wallet_id)
        
        # Try to get more wallet info if possible
        url = f"{circle_api.base_url}/v1/w3s/developer/wallets/{company.circle_wallet_id}"
        headers = circle_api._get_headers()
        
        import requests
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            wallet_data = result.get("data", {}).get("wallet", {})
            
            return WalletInfoResponse(
                wallet_id=company.circle_wallet_id,
                address=wallet_data.get("address") or address,
                state=wallet_data.get("state"),
                wallet_set_id=wallet_data.get("walletSetId") or company.circle_wallet_set_id
            )
        except:
            # Fallback to just address
            return WalletInfoResponse(
                wallet_id=company.circle_wallet_id,
                address=address,
                state=None,
                wallet_set_id=company.circle_wallet_set_id
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wallet info: {str(e)}"
        )


@router.get("/wallet/balances", response_model=WalletBalancesResponse)
async def get_wallet_all_balances(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all token balances for wallet ID from Circle API
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not company.circle_wallet_id:
        raise HTTPException(
            status_code=400, 
            detail="Circle wallet ID not configured. Please set it in company settings."
        )
    
    try:
        url = f"{circle_api.base_url}/v1/w3s/developer/wallets/{company.circle_wallet_id}/balances"
        headers = circle_api._get_headers()
        
        import requests
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        token_balances = result.get("data", {}).get("tokenBalances", [])
        
        balances = []
        for tb in token_balances:
            token = tb.get("token", {})
            balances.append(TokenBalance(
                token_id=token.get("id"),
                token_address=token.get("address"),
                symbol=token.get("symbol", "UNKNOWN"),
                amount=tb.get("amount", "0"),
                decimals=token.get("decimals")
            ))
        
        return WalletBalancesResponse(
            wallet_id=company.circle_wallet_id,
            balances=balances
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wallet balances: {str(e)}"
        )


@router.get("/transaction/{transaction_id}", response_model=TransactionStatusResponse)
async def get_transaction_status(
    transaction_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction status from Circle API by transaction ID
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        tx_data = circle_api.get_transaction_status(transaction_id)
        
        if not tx_data:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found or failed to retrieve"
            )
        
        return TransactionStatusResponse(
            transaction_id=tx_data.get("id", transaction_id),
            state=tx_data.get("state", "UNKNOWN"),
            tx_hash=tx_data.get("txHash"),
            data=tx_data.get("data")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transaction status: {str(e)}"
        )


@router.get("/public-key")
async def get_circle_public_key(
    current_user=Depends(get_current_user)
):
    """
    Get Circle's public key for encryption (useful for frontend)
    """
    try:
        public_key = circle_api.get_public_key()
        return {
            "public_key": public_key,
            "algorithm": "RSA OAEP with SHA-256"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Circle public key: {str(e)}"
        )

