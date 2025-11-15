"""
Dashboard routes: statistics and analytics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Worker, Company, Department, AdditionalSpending, Revenue
from ..schemas import DashboardStats
from ..auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Total workers
    total_workers = db.query(Worker).join(Department).filter(
        Department.company_id == company.id,
        Worker.is_active == True
    ).count()
    
    # Total departments
    total_departments = db.query(Department).filter(
        Department.company_id == company.id
    ).count()
    
    # Total payroll (sum of all active worker salaries)
    total_payroll = db.query(func.sum(Worker.salary)).join(Department).filter(
        Department.company_id == company.id,
        Worker.is_active == True
    ).scalar() or 0.0
    
    # Total additional spendings
    total_spendings = db.query(func.sum(AdditionalSpending.amount)).filter(
        AdditionalSpending.company_id == company.id
    ).scalar() or 0.0
    
    # Total expenses
    total_expenses = total_payroll + total_spendings
    
    # Total revenue
    total_revenue = db.query(func.sum(Revenue.amount)).filter(
        Revenue.company_id == company.id
    ).scalar() or 0.0
    
    # Profit
    profit = total_revenue - total_expenses
    
    # Department statistics
    departments = db.query(Department).filter(Department.company_id == company.id).all()
    department_stats = []
    
    for dept in departments:
        dept_workers = db.query(Worker).filter(
            Worker.department_id == dept.id,
            Worker.is_active == True
        ).all()
        dept_payroll = sum(w.salary for w in dept_workers)
        dept_spendings = db.query(func.sum(AdditionalSpending.amount)).filter(
            AdditionalSpending.department_id == dept.id
        ).scalar() or 0.0
        
        department_stats.append({
            "name": dept.name,
            "worker_count": len(dept_workers),
            "payroll": dept_payroll,
            "spendings": dept_spendings,
            "total": dept_payroll + dept_spendings
        })
    
    return DashboardStats(
        total_workers=total_workers,
        total_departments=total_departments,
        total_revenue=total_revenue,
        total_payroll=total_payroll,
        total_spendings=total_spendings,
        total_expenses=total_expenses,
        profit=profit,
        department_stats=department_stats
    )

