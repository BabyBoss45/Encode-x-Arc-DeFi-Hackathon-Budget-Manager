"""
Department routes: CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Department, Company
from ..schemas import DepartmentCreate, DepartmentResponse
from ..auth import get_current_user
from ..cache import clear_cache

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all departments for user's company"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    departments = db.query(Department).filter(Department.company_id == company.id).all()
    return departments


@router.post("/", response_model=DepartmentResponse)
async def create_department(
    dept_data: DepartmentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new department"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    department = Department(
        company_id=company.id,
        name=dept_data.name
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    
    # Clear dashboard cache since stats changed
    clear_cache(current_user.id)
    
    return department


@router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a department"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    department = db.query(Department).filter(
        Department.id == department_id,
        Department.company_id == company.id
    ).first()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db.delete(department)
    db.commit()
    
    # Clear dashboard cache since stats changed
    clear_cache(current_user.id)
    
    return {"message": "Department deleted"}

