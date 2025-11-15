"""
Worker routes: CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Worker, Department, Company
from ..schemas import WorkerCreate, WorkerUpdate, WorkerResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/workers", tags=["workers"])


@router.get("/", response_model=List[WorkerResponse])
async def get_workers(
    department_id: int = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workers, optionally filtered by department"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    query = db.query(Worker).join(Department).filter(Department.company_id == company.id)
    
    if department_id:
        query = query.filter(Worker.department_id == department_id)
    
    workers = query.all()
    return workers


@router.post("/", response_model=WorkerResponse)
async def create_worker(
    worker_data: WorkerCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new worker"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Verify department belongs to company
    department = db.query(Department).filter(
        Department.id == worker_data.department_id,
        Department.company_id == company.id
    ).first()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Validate wallet address
    if not worker_data.wallet_address.startswith("0x") or len(worker_data.wallet_address) != 42:
        raise HTTPException(status_code=400, detail="Invalid wallet address format")
    
    worker = Worker(
        department_id=worker_data.department_id,
        name=worker_data.name,
        surname=worker_data.surname,
        salary=worker_data.salary,
        wallet_address=worker_data.wallet_address
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.put("/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    worker_data: WorkerUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a worker"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    worker = db.query(Worker).join(Department).filter(
        Worker.id == worker_id,
        Department.company_id == company.id
    ).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Update fields
    if worker_data.name is not None:
        worker.name = worker_data.name
    if worker_data.surname is not None:
        worker.surname = worker_data.surname
    if worker_data.salary is not None:
        worker.salary = worker_data.salary
    if worker_data.wallet_address is not None:
        if not worker_data.wallet_address.startswith("0x") or len(worker_data.wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        worker.wallet_address = worker_data.wallet_address
    if worker_data.is_active is not None:
        worker.is_active = worker_data.is_active
    if worker_data.department_id is not None:
        # Verify new department belongs to company
        department = db.query(Department).filter(
            Department.id == worker_data.department_id,
            Department.company_id == company.id
        ).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        worker.department_id = worker_data.department_id
    
    db.commit()
    db.refresh(worker)
    return worker


@router.delete("/{worker_id}")
async def delete_worker(
    worker_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a worker"""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    worker = db.query(Worker).join(Department).filter(
        Worker.id == worker_id,
        Department.company_id == company.id
    ).first()
    
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    db.delete(worker)
    db.commit()
    return {"message": "Worker deleted"}

