"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime


# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    company_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Company schemas
class CompanyCreate(BaseModel):
    master_wallet_address: Optional[str] = None  # Blockchain address (for display)
    circle_wallet_id: Optional[str] = None  # Circle wallet ID (UUID)
    circle_wallet_set_id: Optional[str] = None  # Circle wallet set ID
    entity_secret: Optional[str] = None  # Entity secret (64 hex chars) - will be encrypted
    payroll_date: Optional[date] = None  # Date for payroll payment
    payroll_time: Optional[str] = None  # Time in 24-hour format (HH:MM)


class CompanyResponse(BaseModel):
    id: int
    master_wallet_address: Optional[str]
    circle_wallet_id: Optional[str] = None
    circle_wallet_set_id: Optional[str] = None
    payroll_date: Optional[date] = None
    payroll_time: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Department schemas
class DepartmentCreate(BaseModel):
    name: str


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: int
    name: str
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Worker schemas
class WorkerCreate(BaseModel):
    name: str
    surname: str
    salary: float
    wallet_address: str
    department_id: int


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    salary: Optional[float] = None
    wallet_address: Optional[str] = None
    is_active: Optional[bool] = None
    department_id: Optional[int] = None


class WorkerResponse(BaseModel):
    id: int
    name: str
    surname: str
    salary: float
    wallet_address: str
    is_active: bool
    department_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Spending schemas
class SpendingCreate(BaseModel):
    name: str
    amount: float
    wallet_address: str
    department_id: Optional[int] = None  # None means assigned to CEO


class SpendingResponse(BaseModel):
    id: int
    name: str
    amount: float
    wallet_address: str
    company_id: int
    department_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Revenue schemas
class RevenueCreate(BaseModel):
    amount: float
    month: int  # 1-12
    year: int


class RevenueResponse(BaseModel):
    id: int
    amount: float
    month: int
    year: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Payroll schemas
class PayrollCreate(BaseModel):
    period_start: date
    period_end: date


class PayrollTransactionResponse(BaseModel):
    id: int
    worker_id: int
    amount: float
    period_start: date
    period_end: date
    status: str  # pending, INITIATED, QUEUED, SENT, CONFIRMED, COMPLETE, failed
    transaction_hash: Optional[str]  # Blockchain transaction hash
    circle_transaction_id: Optional[str] = None  # Circle transaction ID (UUID)
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardStats(BaseModel):
    total_workers: int
    total_departments: int
    total_revenue: float
    total_payroll: float
    total_spendings: float
    total_expenses: float
    profit: float
    wallet_balance: Optional[float] = None  # USDC balance from Circle wallet
    department_stats: List[dict]

