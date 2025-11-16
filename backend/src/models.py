"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="user", uselist=False)


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    master_wallet_address = Column(String, nullable=True)  # Blockchain address for display
    circle_wallet_id = Column(String, nullable=True)  # Circle wallet ID (UUID) for API calls
    circle_wallet_set_id = Column(String, nullable=True)  # Circle wallet set ID
    entity_secret_encrypted = Column(String, nullable=True)  # Encrypted entity secret (base64)
    payroll_date = Column(Date, nullable=True)  # Date for payroll payment
    payroll_time = Column(String, nullable=True)  # Time in 24-hour format (HH:MM)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="company")
    departments = relationship("Department", back_populates="company", cascade="all, delete-orphan")
    spendings = relationship("AdditionalSpending", back_populates="company", cascade="all, delete-orphan")
    revenues = relationship("Revenue", back_populates="company", cascade="all, delete-orphan")
    payroll_transactions = relationship("PayrollTransaction", back_populates="company", cascade="all, delete-orphan")


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="departments")
    workers = relationship("Worker", back_populates="department", cascade="all, delete-orphan")
    spendings = relationship("AdditionalSpending", back_populates="department", cascade="all, delete-orphan")


class Worker(Base):
    __tablename__ = "workers"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    wallet_address = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    department = relationship("Department", back_populates="workers")
    payroll_transactions = relationship("PayrollTransaction", back_populates="worker", cascade="all, delete-orphan")


class AdditionalSpending(Base):
    __tablename__ = "additional_spendings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    wallet_address = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="spendings")
    department = relationship("Department", back_populates="spendings")
    spending_transactions = relationship("SpendingTransaction", back_populates="spending", cascade="all, delete-orphan")


class Revenue(Base):
    __tablename__ = "revenues"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="revenues")


class PayrollTransaction(Base):
    __tablename__ = "payroll_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, completed, failed, INITIATED, QUEUED, SENT, CONFIRMED, COMPLETE
    transaction_hash = Column(String, nullable=True)  # Circle transaction ID or blockchain tx hash
    circle_transaction_id = Column(String, nullable=True)  # Circle transaction ID (UUID)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    company = relationship("Company", back_populates="payroll_transactions")
    worker = relationship("Worker", back_populates="payroll_transactions")


class SpendingTransaction(Base):
    __tablename__ = "spending_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    spending_id = Column(Integer, ForeignKey("additional_spendings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_hash = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)  # pending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    spending = relationship("AdditionalSpending", back_populates="spending_transactions")

