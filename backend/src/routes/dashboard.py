"""
Dashboard routes: statistics and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Worker, Company, Department, AdditionalSpending, Revenue
from ..schemas import DashboardStats
from ..auth import get_current_user
from ..cache import get_cached, set_cache

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    response: Response,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics - optimized with caching and single queries"""
    # Check cache first
    cached_data = get_cached(current_user.id)
    if cached_data:
        response.headers["X-Cache"] = "HIT"
        return cached_data
    
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Optimize: Load departments first (needed for all other queries)
    departments = db.query(Department).filter(Department.company_id == company.id).all()
    
    # Optimize: Pre-load all data in parallel queries (reduces round-trips through ngrok)
    # Load all workers and spendings in one query each
    all_workers = db.query(Worker).join(Department).filter(
        Department.company_id == company.id,
        Worker.is_active == True
    ).all()
    
    all_spendings = db.query(AdditionalSpending).filter(
        AdditionalSpending.company_id == company.id
    ).all()
    
    all_revenues = db.query(Revenue).filter(
        Revenue.company_id == company.id
    ).all()
    
    # Calculate statistics from pre-loaded data (no additional DB queries)
    total_workers = len(all_workers)
    total_departments = len(departments)
    total_payroll = sum(w.salary for w in all_workers) or 0.0
    total_spendings = sum(s.amount for s in all_spendings) or 0.0
    total_expenses = total_payroll + total_spendings
    total_revenue = sum(r.amount for r in all_revenues) or 0.0
    profit = total_revenue - total_expenses
    
    # Create lookup dictionaries for O(1) access
    workers_by_dept = {}
    for worker in all_workers:
        dept_id = worker.department_id
        if dept_id not in workers_by_dept:
            workers_by_dept[dept_id] = []
        workers_by_dept[dept_id].append(worker)
    
    spendings_by_dept = {}
    for spending in all_spendings:
        dept_id = spending.department_id
        if dept_id:
            if dept_id not in spendings_by_dept:
                spendings_by_dept[dept_id] = []
            spendings_by_dept[dept_id].append(spending)
    
    # Build department stats using pre-loaded data
    department_stats = []
    for dept in departments:
        dept_workers = workers_by_dept.get(dept.id, [])
        dept_payroll = sum(w.salary for w in dept_workers)
        dept_spendings_list = spendings_by_dept.get(dept.id, [])
        dept_spendings = sum(s.amount for s in dept_spendings_list)
        
        department_stats.append({
            "name": dept.name,
            "worker_count": len(dept_workers),
            "payroll": dept_payroll,
            "spendings": dept_spendings,
            "total": dept_payroll + dept_spendings
        })
    
    result = DashboardStats(
        total_workers=total_workers,
        total_departments=total_departments,
        total_revenue=total_revenue,
        total_payroll=total_payroll,
        total_spendings=total_spendings,
        total_expenses=total_expenses,
        profit=profit,
        department_stats=department_stats
    )
    
    # Cache the result
    set_cache(current_user.id, result)
    
    response.headers["X-Cache"] = "MISS"
    
    return result

