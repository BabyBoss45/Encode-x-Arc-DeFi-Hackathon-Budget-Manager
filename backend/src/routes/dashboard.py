"""
Dashboard routes: statistics and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime
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
    
    # Get USDC wallet balance from Circle API if configured
    wallet_balance = None
    if company.circle_wallet_id:
        print(f"[DASHBOARD] Getting balance for wallet_id: {company.circle_wallet_id}")
        try:
            from ..circle_api import circle_api
            # Use the new get_usdc_balance method which uses wallets/balances endpoint
            wallet_balance = circle_api.get_usdc_balance(company.circle_wallet_id)
            print(f"[DASHBOARD] ✓ CEO wallet balance retrieved: {wallet_balance} USDC (type: {type(wallet_balance)})")
        except Exception as e:
            # Don't fail dashboard if balance check fails
            print(f"[DASHBOARD] ✗ Warning: Could not get wallet balance: {e}")
            import traceback
            traceback.print_exc()
            wallet_balance = None
    else:
        print(f"[DASHBOARD] ⚠ No circle_wallet_id configured for company {company.id}")
    
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
        wallet_balance=wallet_balance,
        department_stats=department_stats
    )
    
    # Cache the result
    set_cache(current_user.id, result)
    
    response.headers["X-Cache"] = "MISS"
    
    return result


@router.get("/transactions")
async def get_circle_transactions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Circle API transactions for the company wallet"""
    try:
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        if not company or not company.circle_wallet_id:
            return []
        
        # Get transactions from Circle API
        try:
            from ..circle_api import circle_api
            transactions = circle_api.get_wallet_transactions(company.circle_wallet_id)
            print(f"[DEBUG] Got {len(transactions) if transactions else 0} transactions from Circle API")
            if transactions and len(transactions) > 0:
                print(f"[DEBUG] First transaction keys: {list(transactions[0].keys())}")
                print(f"[DEBUG] First transaction sample: {transactions[0]}")
            if not transactions:
                return []
        except Exception as e:
            # If Circle API fails, return empty list instead of crashing
            print(f"Warning: Could not fetch Circle transactions: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        # Format transactions for frontend
        formatted_transactions = []
        for tx in transactions:
            try:
                # Skip None or invalid transactions
                if not tx or not isinstance(tx, dict):
                    continue
                
                # Debug: print transaction structure
                print(f"[DEBUG] Processing transaction: {tx.get('id', 'no-id')}")
                print(f"[DEBUG] Transaction keys: {list(tx.keys())}")
                
                # Extract transaction data from Circle API response
                # Get transaction type - check multiple possible fields
                tx_type_raw = (
                    tx.get("type", "") or 
                    tx.get("transactionType", "") or 
                    tx.get("txType", "") or
                    ""
                )
                if isinstance(tx_type_raw, dict):
                    tx_type_raw = tx_type_raw.get("type", "") or ""
                tx_type_raw = str(tx_type_raw).lower()
                
                print(f"[DEBUG] Raw transaction type: '{tx_type_raw}'")
                
                tx_type_display = "Unknown"
                if tx_type_raw in ["deposit", "incoming", "receive", "credit"]:
                    tx_type_display = "Deposit"
                elif tx_type_raw in ["withdrawal", "outgoing", "withdraw", "debit"]:
                    tx_type_display = "Withdrawal"
                elif tx_type_raw in ["transfer", "send", "payment"]:
                    tx_type_display = "Transfer"
                elif tx_type_raw:
                    tx_type_display = tx_type_raw.capitalize()
                
                # Get transaction status/state - check multiple possible fields
                state_raw = (
                    tx.get("state", "") or 
                    tx.get("status", "") or 
                    tx.get("transactionState", "") or
                    ""
                )
                if isinstance(state_raw, dict):
                    state_raw = state_raw.get("state", "") or state_raw.get("status", "") or ""
                state_raw = str(state_raw).lower()
                
                print(f"[DEBUG] Raw transaction state: '{state_raw}'")
                
                state_display = "Unknown"
                if state_raw in ["complete", "completed", "settled", "confirmed", "success"]:
                    state_display = "Complete"
                elif state_raw in ["pending", "queued", "initiated", "processing"]:
                    state_display = "Pending"
                elif state_raw in ["failed", "error", "rejected"]:
                    state_display = "Failed"
                elif state_raw:
                    state_display = state_raw.capitalize()
                
                print(f"[DEBUG] Formatted: type='{tx_type_display}', status='{state_display}'")
                
                # Get amount and currency
                amount_data = tx.get("amount", {})
                if not amount_data or not isinstance(amount_data, dict):
                    amount_data = {}
                amount = float(amount_data.get("amount", 0) or 0)
                currency = str(amount_data.get("currency", "USDC") or "USDC")
            
                # Get date with time
                created_at = tx.get("createDate", "") or tx.get("createdAt", "") or tx.get("updateDate", "")
                formatted_date = "N/A"
                if created_at:
                    try:
                        # Parse ISO format date
                        date_obj = None
                        if "T" in str(created_at):
                            date_str = str(created_at).split("T")[0]
                            time_part = str(created_at).split("T")[1]
                            time_str = time_part.split(".")[0].split("+")[0].split("Z")[0]
                            try:
                                date_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                            except:
                                # Try with microseconds
                                if "." in time_part:
                                    time_str = time_part.split("+")[0].split("Z")[0]
                                    date_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S.%f")
                        else:
                            date_obj = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
                        
                        if date_obj:
                            # Format: "Jan 27, 2025, 1:56 PM" (with time!)
                            day = date_obj.strftime("%d").lstrip("0") or "1"
                            month = date_obj.strftime("%b")
                            year = date_obj.strftime("%Y")
                            hour = date_obj.strftime("%I").lstrip("0") or "12"
                            minute = date_obj.strftime("%M")
                            ampm = date_obj.strftime("%p")
                            formatted_date = f"{month} {day}, {year}, {hour}:{minute} {ampm}"
                        else:
                            formatted_date = str(created_at)[:19] if len(str(created_at)) > 19 else str(created_at)
                    except Exception as e:
                        # Fallback: try to extract date and time from string
                        try:
                            if "T" in str(created_at):
                                parts = str(created_at).split("T")
                                date_part = parts[0]
                                time_part = parts[1].split(".")[0].split("+")[0].split("Z")[0]
                                formatted_date = f"{date_part} {time_part}"
                            else:
                                formatted_date = str(created_at)[:19] if len(str(created_at)) > 19 else str(created_at)
                        except:
                            formatted_date = str(created_at)[:19] if len(str(created_at)) > 19 else str(created_at)
                
                # Determine if it's incoming or outgoing based on transaction type
                # Use the already formatted tx_type_display
                if tx_type_display == "Deposit":
                    is_incoming = True
                elif tx_type_display in ["Withdrawal", "Transfer"]:
                    is_incoming = False
                else:
                    # Fallback: check state and amount
                    state = str(tx.get("state", "")).lower()
                    is_incoming = state in ["complete", "confirmed", "settled"] and amount > 0
                
                # Format amount string based on currency
                if currency in ["BTC", "ETH"]:
                    amount_str = f"{abs(amount):.7f}".rstrip('0').rstrip('.')
                else:
                    amount_str = f"{abs(amount):.2f}"
                
                formatted_transactions.append({
                    "transaction_type": tx_type_display,
                    "transaction_status": state_display,
                    "date": formatted_date,
                    "amount": abs(amount),
                    "amount_formatted": amount_str,
                    "currency": currency,
                    "is_incoming": is_incoming,
                    "state": state,
                    # Keep original IDs for reference if needed
                    "transaction_id": str(tx.get("id", "") or tx.get("transactionHash", "") or ""),
                    "reference_id": str(tx.get("idempotencyKey", "") or tx.get("referenceId", "") or "")
                })
            except Exception as e:
                # Skip invalid transactions instead of crashing
                print(f"Warning: Skipping invalid transaction: {e}")
                continue
        
        # Sort by date (newest first)
        try:
            def get_sort_key(tx_dict):
                date_str = tx_dict.get("date", "")
                # Try to parse date for sorting
                try:
                    # Extract date from formatted string like "Jan 27, 2025, 1:56 PM"
                    parts = date_str.split(",")
                    if len(parts) >= 2:
                        month_day = parts[0].strip()
                        year = parts[1].strip().split()[0]
                        # Convert to sortable format
                        return f"{year}-{month_day}"
                except:
                    pass
                return date_str
            
            formatted_transactions.sort(key=get_sort_key, reverse=True)
        except:
            # If sorting fails, just return unsorted list
            pass
        
        return formatted_transactions
    except Exception as e:
        # Return empty list on any error instead of crashing
        print(f"Error in get_circle_transactions: {e}")
        return []

