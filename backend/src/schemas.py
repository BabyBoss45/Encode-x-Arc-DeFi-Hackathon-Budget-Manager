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
    master_wallet_address: str
    payroll_date: Optional[date] = None  # Date for payroll payment
    payroll_time: Optional[str] = None  # Time in 24-hour format (HH:MM)


class CompanyResponse(BaseModel):
    id: int
    master_wallet_address: Optional[str]
    payroll_date: Optional[date] = None
    payroll_time: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Department schemas
class DepartmentCreate(BaseModel):
    name: str


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
    status: str
    transaction_hash: Optional[str]
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
    department_stats: List[dict]

