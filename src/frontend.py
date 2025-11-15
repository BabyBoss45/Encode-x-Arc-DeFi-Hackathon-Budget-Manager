"""
ARC budget Frontend with FastAPI
Integrated with Backend API for persistent data storage
"""
from fastapi import FastAPI, Request, Form, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
try:
    from .api_client import APIClient
except ImportError:
    from api_client import APIClient
import os
import json

# Create application
app = FastAPI(title="ARC budget Frontend")

# Setup for static files (CSS, JS, images)
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

# Create folders if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Mount static files
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates = Jinja2Templates(directory=templates_dir)

# API Client
api_client = APIClient()

# Fallback in-memory storage (if backend is not available)
fallback_data = {
    "users": {},
    "organization": {
        "ceo": None,
        "departments": {},
        "workers": {},
        "spendings": [],
        "revenues": []
    },
    "next_dept_id": 1,
    "next_worker_id": 1,
    "next_spending_id": 1
}


def get_token_from_request(request: Request) -> str | None:
    """Get JWT token from cookie"""
    return request.cookies.get("access_token")


def set_api_token(token: str):
    """Set token for API client"""
    api_client.set_token(token)


def check_backend_available() -> bool:
    """Check if backend is available"""
    try:
        import requests
        base_url = api_client.base_url.replace('/api', '')
        resp = requests.get(f"{base_url}/health", timeout=2)
        return resp.status_code == 200
    except:
        return False


# Root page - redirect to login
@app.get("/")
async def root():
    return RedirectResponse(url="/login")


# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Handle login
@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # Basic email validation
    if "@" not in email or "." not in email.split("@")[1]:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email format"}
        )
    
    # Try backend API first
    use_backend = check_backend_available()
    
    if use_backend:
        try:
            result = api_client.login(email, password)
            token = result.get("access_token")
            if token:
                response = RedirectResponse(url="/constructor", status_code=303)
                response.set_cookie(key="access_token", value=token, httponly=True, max_age=1800)
                return response
        except Exception as e:
            error_msg = "Invalid email or password"
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": error_msg}
            )
    else:
        # Fallback to in-memory
        email_lower = email.lower().strip()
        if email_lower in fallback_data["users"] and fallback_data["users"][email_lower]["password"] == password:
            return RedirectResponse(url="/constructor", status_code=303)
        else:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid email or password"}
            )


# Sign Up page
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


# Handle sign up (register)
@app.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    company_name: str = Form(...)
):
    # Basic email validation
    if "@" not in email or "." not in email.split("@")[1]:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Invalid email format"}
        )
    
    # Validate password length
    if len(password) < 6:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Password must be at least 6 characters"}
        )
    
    # Validate company name
    if not company_name.strip():
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Company name is required"}
        )
    
    # Try backend API first
    use_backend = check_backend_available()
    
    if use_backend:
        try:
            result = api_client.register(email, password, company_name)
            token = result.get("access_token")
            if token:
                response = RedirectResponse(url="/login?registered=true", status_code=303)
                response.set_cookie(key="access_token", value=token, httponly=True, max_age=1800)
                return response
        except Exception as e:
            error_msg = "Registration failed"
            if hasattr(e, 'response') and hasattr(e.response, 'json'):
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("detail", error_msg)
                except:
                    pass
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": error_msg}
            )
    else:
        # Fallback to in-memory
        email_lower = email.lower().strip()
        if email_lower in fallback_data["users"]:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Email already registered"}
            )
        
        fallback_data["users"][email_lower] = {
            "password": password,
            "company_name": company_name.strip()
        }
        return RedirectResponse(url="/login?registered=true", status_code=303)


# Constructor page
@app.get("/constructor", response_class=HTMLResponse)
async def constructor_page(request: Request):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    try:
        if use_backend:
            set_api_token(token)
            # Initialize payroll_transactions
            payroll_transactions = []
            # Get data from API
            try:
                company = api_client.get_company()
                departments = api_client.get_departments()
                workers = api_client.get_workers()
                spendings = api_client.get_spendings()
                revenues = api_client.get_revenues()
                try:
                    payroll_transactions = api_client.get_payroll_transactions()
                except:
                    payroll_transactions = []
                
                # Transform API data to template format
                import random
                from datetime import datetime, timedelta
                departments_list = []
                for dept in departments:
                    dept_workers = [w for w in workers if w.get("department_id") == dept.get("id")]
                    # Add additional worker info for modal
                    for worker in dept_workers:
                        # Add years in company (default: 1-5 years, or from created_at if available)
                        if "created_at" in worker:
                            try:
                                created = datetime.fromisoformat(worker["created_at"].replace("Z", "+00:00"))
                                years = (datetime.now() - created.replace(tzinfo=None)).days / 365.25
                                worker["years_in_company"] = max(1, int(years))
                            except:
                                worker["years_in_company"] = random.randint(1, 5)
                        else:
                            worker["years_in_company"] = random.randint(1, 5)
                        
                        # Add salary change percentage (default: -10% to +15%)
                        if "salary_change" not in worker:
                            worker["salary_change"] = round(random.uniform(-10, 15), 1)
                    
                    dept_spendings = [s for s in spendings if s.get("department_id") == dept.get("id")]
                    
                    departments_list.append({
                        "id": dept.get("id"),
                        "name": dept.get("name", ""),
                        "worker_count": len(dept_workers),
                        "total_spendings": sum(w.get("salary", 0) for w in dept_workers) + sum(s.get("amount", 0) for s in dept_spendings),
                        "workers": dept_workers,
                        "spendings": dept_spendings
                    })
                
                ceo_spendings = [s for s in spendings if s.get("department_id") is None]
                ceo_data = {
                    "master_wallet": company.get("master_wallet_address", ""),
                    "payroll_frequency": "Monthly",  # Default
                    "payroll_date": company.get("payroll_date"),
                    "payroll_time": company.get("payroll_time")
                } if company.get("master_wallet_address") else None
                
                # Transform revenues
                revenues_list = [{"month": f"{r.get('year', '')}-{r.get('month', ''):02d}", "amount": r.get("amount", 0)} for r in revenues]
                
            except Exception as e:
                # If API fails, use empty data
                departments_list = []
                ceo_data = None
                ceo_spendings = []
                revenues_list = []
                payroll_transactions = []
        else:
            # Fallback to in-memory
            import random
            org = fallback_data["organization"]
            departments_list = []
            for dept_id, dept in org["departments"].items():
                workers_in_dept = [w for w in org["workers"].values() if w.get("department_id") == dept_id]
                # Add additional worker info for modal
                for worker in workers_in_dept:
                    # Add years in company (default: 1-5 years)
                    if "years_in_company" not in worker:
                        worker["years_in_company"] = random.randint(1, 5)
                    
                    # Add salary change percentage (default: -10% to +15%)
                    if "salary_change" not in worker:
                        worker["salary_change"] = round(random.uniform(-10, 15), 1)
                
                dept_spendings = [s for s in org["spendings"] if s.get("target_type") == f"dept_{dept_id}"]
                total_spendings = sum(w.get("salary", 0) for w in workers_in_dept) + sum(s.get("amount", 0) for s in dept_spendings)
                
                departments_list.append({
                    "id": dept_id,
                    "name": dept.get("name", ""),
                    "worker_count": len(workers_in_dept),
                    "total_spendings": total_spendings,
                    "workers": workers_in_dept,
                    "spendings": dept_spendings
                })
            
            ceo_spendings = [s for s in org["spendings"] if s.get("target_type") == "ceo"]
            ceo_data = org["ceo"]
            revenues_list = org["revenues"]
        
        return templates.TemplateResponse("constructor.html", {
            "request": request,
            "ceo_data": ceo_data,
            "ceo_spendings": ceo_spendings,
            "departments": departments_list,
            "revenues": revenues_list
        })
    except Exception as e:
        return templates.TemplateResponse("constructor.html", {
            "request": request,
            "ceo_data": None,
            "ceo_spendings": [],
            "departments": [],
            "revenues": [],
            "error": f"Error loading page: {str(e)}"
        })


# Handle CEO/Master Wallet
@app.post("/constructor/ceo")
async def save_ceo(request: Request, 
                   master_wallet: str = Form(...), 
                   payroll_frequency: str = Form(...),
                   payroll_date: str = Form(None),
                   payroll_time: str = Form(None)):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    if not master_wallet.startswith("0x") or len(master_wallet) != 42:
        return RedirectResponse(url="/constructor?error=Invalid wallet address format", status_code=303)
    
    # Parse payroll_date
    payroll_date_obj = None
    if payroll_date and payroll_date.strip():
        try:
            from datetime import datetime
            payroll_date_obj = datetime.strptime(payroll_date, "%Y-%m-%d").date()
        except ValueError:
            return RedirectResponse(url="/constructor?error=Invalid payroll date format", status_code=303)
    
    # Validate payroll_time format
    if payroll_time and payroll_time.strip():
        try:
            parts = payroll_time.split(":")
            if len(parts) != 2:
                raise ValueError
            hour = int(parts[0])
            minute = int(parts[1])
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError
        except (ValueError, IndexError):
            return RedirectResponse(url="/constructor?error=Payroll time must be in HH:MM format (24-hour)", status_code=303)
    
    if use_backend:
        try:
            set_api_token(token)
            # Update master wallet with payroll date and time
            import requests
            response = requests.put(
                f"{api_client.base_url}/company/master-wallet",
                json={
                    "master_wallet_address": master_wallet,
                    "payroll_date": payroll_date_obj.isoformat() if payroll_date_obj else None,
                    "payroll_time": payroll_time if payroll_time and payroll_time.strip() else None
                },
                headers=api_client._get_headers()
            )
            response.raise_for_status()
        except Exception as e:
            return RedirectResponse(url="/constructor?error=Failed to save settings", status_code=303)
    else:
        # Fallback
        fallback_data["organization"]["ceo"] = {
            "master_wallet": master_wallet,
            "payroll_frequency": payroll_frequency,
            "payroll_date": payroll_date if payroll_date and payroll_date.strip() else None,
            "payroll_time": payroll_time if payroll_time and payroll_time.strip() else None
        }
    
    return RedirectResponse(url="/constructor", status_code=303)


# Handle Department creation
@app.post("/constructor/department")
async def create_department(request: Request, name: str = Form(...)):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    if not name.strip():
        return RedirectResponse(url="/constructor?error=Department name required", status_code=303)
    
    if use_backend:
        try:
            set_api_token(token)
            api_client.create_department(name.strip())
        except Exception as e:
            return RedirectResponse(url="/constructor?error=Failed to create department", status_code=303)
    else:
        # Fallback
        dept_id = fallback_data["next_dept_id"]
        fallback_data["organization"]["departments"][dept_id] = {
            "name": name.strip(),
            "workers": [],
            "spendings": []
        }
        fallback_data["next_dept_id"] += 1
    
    return RedirectResponse(url="/constructor", status_code=303)


# Handle Worker creation
@app.post("/constructor/worker")
async def create_worker(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    salary: str = Form(...),
    wallet: str = Form(...),
    department_id: str = Form(...)
):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    try:
        salary_float = float(salary)
        dept_id = int(department_id)
    except ValueError:
        return RedirectResponse(url="/constructor?error=Invalid input", status_code=303)
    
    if not wallet.startswith("0x") or len(wallet) != 42:
        return RedirectResponse(url="/constructor?error=Invalid wallet address", status_code=303)
    
    if use_backend:
        try:
            set_api_token(token)
            api_client.create_worker(name.strip(), surname.strip(), salary_float, wallet.strip(), dept_id)
        except Exception as e:
            return RedirectResponse(url="/constructor?error=Failed to create worker", status_code=303)
    else:
        # Fallback
        if dept_id not in fallback_data["organization"]["departments"]:
            return RedirectResponse(url="/constructor?error=Department not found", status_code=303)
        
        worker_id = fallback_data["next_worker_id"]
        fallback_data["organization"]["workers"][worker_id] = {
            "name": name.strip(),
            "surname": surname.strip(),
            "salary": salary_float,
            "wallet": wallet.strip(),
            "department_id": dept_id
        }
        fallback_data["next_worker_id"] += 1
    
    return RedirectResponse(url="/constructor", status_code=303)


# Handle Department deletion
@app.post("/constructor/department/{dept_id}/delete")
async def delete_department(request: Request, dept_id: int):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    if use_backend:
        try:
            set_api_token(token)
            # Try to delete via API if method exists
            try:
                api_client.delete_department(dept_id)
            except AttributeError:
                # If method doesn't exist, try direct API call
                import requests
                response = requests.delete(
                    f"{api_client.base_url}/departments/{dept_id}",
                    headers=api_client._get_headers()
                )
                response.raise_for_status()
        except Exception as e:
            return RedirectResponse(url="/constructor?error=Failed to delete department", status_code=303)
    else:
        # Fallback
        if dept_id in fallback_data["organization"]["departments"]:
            # Remove all workers from this department
            workers_to_remove = [
                wid for wid, worker in fallback_data["organization"]["workers"].items()
                if worker.get("department_id") == dept_id
            ]
            for wid in workers_to_remove:
                del fallback_data["organization"]["workers"][wid]
            # Remove department
            del fallback_data["organization"]["departments"][dept_id]
    
    return RedirectResponse(url="/constructor", status_code=303)


# Handle Worker deletion
@app.post("/constructor/worker/{worker_id}/delete")
async def delete_worker(request: Request, worker_id: int):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    if use_backend:
        try:
            set_api_token(token)
            # Try to delete via API if method exists
            try:
                api_client.delete_worker(worker_id)
            except AttributeError:
                # If method doesn't exist, try direct API call
                import requests
                response = requests.delete(
                    f"{api_client.base_url}/workers/{worker_id}",
                    headers=api_client._get_headers()
                )
                response.raise_for_status()
        except Exception as e:
            return RedirectResponse(url="/constructor?error=Failed to delete worker", status_code=303)
    else:
        # Fallback
        if worker_id in fallback_data["organization"]["workers"]:
            del fallback_data["organization"]["workers"][worker_id]
    
    return RedirectResponse(url="/constructor", status_code=303)


# Handle Additional Spending
@app.post("/constructor/spending")
async def create_spending(
    request: Request,
    name: str = Form(...),
    amount: str = Form(...),
    wallet: str = Form(...),
    target_type: str = Form(...)
):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    try:
        amount_float = float(amount)
    except ValueError:
        return RedirectResponse(url="/constructor?error=Invalid amount", status_code=303)
    
    if not wallet.startswith("0x") or len(wallet) != 42:
        return RedirectResponse(url="/constructor?error=Invalid wallet address", status_code=303)
    
    if use_backend:
        try:
            set_api_token(token)
            dept_id = None
            if target_type.startswith("dept_"):
                dept_id = int(target_type.split("_")[1])
            api_client.create_spending(name.strip(), amount_float, wallet.strip(), dept_id)
        except Exception as e:
            return RedirectResponse(url="/constructor?error=Failed to create spending", status_code=303)
    else:
        # Fallback
        spending = {
            "id": fallback_data["next_spending_id"],
            "name": name.strip(),
            "amount": amount_float,
            "wallet": wallet.strip(),
            "target_type": target_type
        }
        fallback_data["organization"]["spendings"].append(spending)
        fallback_data["next_spending_id"] += 1
    
    return RedirectResponse(url="/constructor", status_code=303)


# Handle Revenue
@app.post("/api/expenses/update-date")
async def update_expense_date(request: Request):
    """Update expense date (for spending or payroll)"""
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    if not use_backend:
        return JSONResponse({"success": False, "message": "Backend not available"})
    
    try:
        data = await request.json()
        expense_id = data.get("expense_id")
        expense_type = data.get("expense_type")
        date = data.get("date")
        
        if not expense_id or not expense_type or not date:
            return JSONResponse({"success": False, "message": "Missing required fields"}, status_code=400)
        
        set_api_token(token)
        
        if expense_type == "spending":
            # Update spending date via API
            try:
                api_client.update_spending_date(expense_id, date)
                return JSONResponse({"success": True, "message": "Date updated"})
            except Exception as e:
                return JSONResponse({"success": False, "message": str(e)}, status_code=500)
        elif expense_type == "payroll":
            # For payroll, dates come from PayrollTransaction
            # We could create/update transaction here if needed
            return JSONResponse({"success": True, "message": "Payroll date noted"})
        else:
            return JSONResponse({"success": False, "message": "Unknown expense type"}, status_code=400)
            
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


@app.post("/constructor/revenue")
async def add_revenue(request: Request, month: str = Form(...), amount: str = Form(...)):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    try:
        amount_float = float(amount)
        # Parse month string (format: "2024-01" or "January 2024")
        if "-" in month:
            year, month_num = month.split("-")
            year = int(year)
            month_num = int(month_num)
        else:
            # Default to current year/month if can't parse
            from datetime import datetime
            now = datetime.now()
            year = now.year
            month_num = now.month
    except (ValueError, AttributeError):
        return RedirectResponse(url="/constructor?error=Invalid amount or month format", status_code=303)
    
    if use_backend:
        try:
            set_api_token(token)
            api_client.create_revenue(amount_float, month_num, year)
        except Exception as e:
            return RedirectResponse(url="/constructor?error=Failed to add revenue", status_code=303)
    else:
        # Fallback
        fallback_data["organization"]["revenues"].append({
            "month": month,
            "amount": amount_float
        })
    
    return RedirectResponse(url="/constructor", status_code=303)


# Dashboard page with statistics
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = get_token_from_request(request)
    use_backend = check_backend_available() and token
    
    try:
        if use_backend:
            set_api_token(token)
            # Get stats from API
            try:
                stats = api_client.get_dashboard_stats()
                departments = api_client.get_departments()
                workers = api_client.get_workers()
                spendings = api_client.get_spendings()
                revenues = api_client.get_revenues()
                try:
                    payroll_transactions = api_client.get_payroll_transactions()
                except:
                    payroll_transactions = []
                
                # Transform for template
                dept_stats = []
                for dept in departments:
                    dept_workers = [w for w in workers if w.get("department_id") == dept.get("id") and w.get("is_active", True)]
                    dept_payroll = sum(w.get("salary", 0) for w in dept_workers)
                    dept_spendings_list = [s for s in spendings if s.get("department_id") == dept.get("id")]
                    dept_spendings_amount = sum(s.get("amount", 0) for s in dept_spendings_list)
                    
                    dept_stats.append({
                        "name": dept.get("name", ""),
                        "worker_count": len(dept_workers),
                        "payroll": dept_payroll,
                        "spendings": dept_spendings_amount,
                        "total": dept_payroll + dept_spendings_amount,
                        "workers": dept_workers
                    })
                
                company = api_client.get_company()
                ceo_data = {
                    "master_wallet": company.get("master_wallet_address", "")
                } if company.get("master_wallet_address") else None
                
                revenues_list = [{"month": f"{r.get('year', '')}-{r.get('month', ''):02d}", "amount": r.get("amount", 0)} for r in revenues]
                
                expenses_list = []
                # Create a map of worker_id to latest payroll transaction date
                worker_payroll_dates = {}
                for transaction in payroll_transactions:
                    worker_id = transaction.get("worker_id")
                    if worker_id:
                        # Get the most recent transaction date for each worker
                        transaction_date = transaction.get("created_at") or transaction.get("period_end")
                        if transaction_date:
                            # Extract date part if it's a datetime string
                            if isinstance(transaction_date, str):
                                transaction_date = transaction_date.split("T")[0] if "T" in transaction_date else transaction_date
                            # Keep the most recent date for each worker
                            if worker_id not in worker_payroll_dates or transaction_date > worker_payroll_dates[worker_id]:
                                worker_payroll_dates[worker_id] = transaction_date
                
                for worker in workers:
                    if worker.get("is_active", True):
                        dept_name = "Unknown"
                        for dept in departments:
                            if dept.get("id") == worker.get("department_id"):
                                dept_name = dept.get("name", "Unknown")
                                break
                        
                        # Get payroll date from transaction, or use worker created_at, or current date
                        from datetime import datetime
                        worker_id = worker.get("id")
                        payroll_date = None
                        
                        if worker_id in worker_payroll_dates:
                            payroll_date = worker_payroll_dates[worker_id]
                        elif worker.get("created_at"):
                            # Use worker creation date as fallback
                            created_at = worker.get("created_at")
                            if isinstance(created_at, str):
                                payroll_date = created_at.split("T")[0] if "T" in created_at else created_at
                            else:
                                payroll_date = datetime.now().date().isoformat()
                        else:
                            payroll_date = datetime.now().date().isoformat()
                        
                        expenses_list.append({
                            "type": "Payroll",
                            "name": f"{worker.get('name', '')} {worker.get('surname', '')} ({dept_name})",
                            "amount": worker.get("salary", 0),
                            "date": payroll_date,
                            "worker_id": worker_id,
                            "expense_id": worker_id,
                            "expense_type": "payroll"
                        })
                
                for spending in spendings:
                    # Get date from spending (if available) or use current date
                    from datetime import datetime
                    expense_date = spending.get("created_at", datetime.now().isoformat())
                    if isinstance(expense_date, str):
                        # Extract date part if it's a datetime string
                        expense_date = expense_date.split("T")[0] if "T" in expense_date else expense_date
                    elif hasattr(expense_date, "date"):
                        expense_date = expense_date.date().isoformat()
                    else:
                        expense_date = datetime.now().date().isoformat()
                    
                    expenses_list.append({
                        "type": "Spending",
                        "name": spending.get("name", ""),
                        "amount": spending.get("amount", 0),
                        "date": expense_date,
                        "spending_id": spending.get("id"),
                        "expense_id": spending.get("id"),
                        "expense_type": "spending"
                    })
                
                return templates.TemplateResponse("dashboard.html", {
                    "request": request,
                    "total_workers": stats.get("total_workers", 0),
                    "total_departments": stats.get("total_departments", 0),
                    "total_payroll": stats.get("total_payroll", 0),
                    "total_spendings": stats.get("total_spendings", 0),
                    "total_expenses": stats.get("total_expenses", 0),
                    "total_revenue": stats.get("total_revenue", 0),
                    "profit": stats.get("profit", 0),
                    "dept_stats": dept_stats,
                    "ceo_data": ceo_data,
                    "revenues_list": revenues_list,
                    "expenses_list": expenses_list
                })
            except Exception as e:
                # If API fails, show empty dashboard
                return templates.TemplateResponse("dashboard.html", {
                    "request": request,
                    "total_workers": 0,
                    "total_departments": 0,
                    "total_payroll": 0,
                    "total_spendings": 0,
                    "total_expenses": 0,
                    "total_revenue": 0,
                    "profit": 0,
                    "dept_stats": [],
                    "ceo_data": None,
                    "revenues_list": [],
                    "expenses_list": []
                })
        else:
            # Fallback to in-memory
            org = fallback_data["organization"]
            total_workers = len(org["workers"])
            total_departments = len(org["departments"])
            total_payroll = sum(w["salary"] for w in org["workers"].values())
            total_spendings = sum(s["amount"] for s in org["spendings"])
            total_expenses = total_payroll + total_spendings
            total_revenue = sum(r["amount"] for r in org["revenues"])
            profit = total_revenue - total_expenses
            
            dept_stats = []
            for dept_id, dept in org["departments"].items():
                workers_in_dept = [w for w in org["workers"].values() if w["department_id"] == dept_id]
                dept_payroll = sum(w["salary"] for w in workers_in_dept)
                dept_spendings = sum(s["amount"] for s in org["spendings"] if s["target_type"] == f"dept_{dept_id}")
                dept_stats.append({
                    "name": dept["name"],
                    "worker_count": len(workers_in_dept),
                    "payroll": dept_payroll,
                    "spendings": dept_spendings,
                    "total": dept_payroll + dept_spendings,
                    "workers": workers_in_dept
                })
            
            revenues_list = org["revenues"]
            expenses_list = []
            for worker_id, worker in org["workers"].items():
                dept_name = "Unknown"
                for dept_id, dept in org["departments"].items():
                    if dept_id == worker.get("department_id"):
                        dept_name = dept.get("name", "Unknown")
                        break
                from datetime import datetime
                expenses_list.append({
                    "type": "Payroll",
                    "name": f"{worker.get('name', '')} {worker.get('surname', '')} ({dept_name})",
                    "amount": worker.get("salary", 0),
                    "date": datetime.now().date().isoformat()
                })
            
            for spending in org["spendings"]:
                from datetime import datetime
                expenses_list.append({
                    "type": "Spending",
                    "name": spending.get("name", ""),
                    "amount": spending.get("amount", 0),
                    "date": datetime.now().date().isoformat()
                })
            
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "total_workers": total_workers,
                "total_departments": total_departments,
                "total_payroll": total_payroll,
                "total_spendings": total_spendings,
                "total_expenses": total_expenses,
                "total_revenue": total_revenue,
                "profit": profit,
                "dept_stats": dept_stats,
                "ceo_data": org["ceo"],
                "revenues_list": revenues_list,
                "expenses_list": expenses_list
            })
    except Exception as e:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_workers": 0,
            "total_departments": 0,
            "total_payroll": 0,
            "total_spendings": 0,
            "total_expenses": 0,
            "total_revenue": 0,
            "profit": 0,
            "dept_stats": [],
            "ceo_data": None,
            "revenues_list": [],
            "expenses_list": [],
            "error": str(e)
        })


if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Try to find an available port
    def find_free_port(start_port=8001):
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                continue
        return start_port
    
    port = find_free_port(8001)
    print(f"🚀 Starting ARC budget frontend on http://localhost:{port}")
    print(f"📝 Open in browser: http://localhost:{port}/login")
    print(f"💡 Make sure backend is running on http://localhost:8000 for data persistence")
    uvicorn.run(app, host="0.0.0.0", port=port)
