"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
from src.database import engine, Base, SessionLocal
from src.routes import auth, company, departments, workers, spendings, revenue, payroll, dashboard, circle
from src.payroll_scheduler import check_and_execute_payrolls
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Scheduler for payroll automation
scheduler = AsyncIOScheduler()


def run_payroll_check():
    """Background task to check and execute scheduled payrolls"""
    db = SessionLocal()
    try:
        results = check_and_execute_payrolls(db)
        if results:
            print(f"[PAYROLL SCHEDULER] Checked {len(results)} companies")
            for result in results:
                if result.get("success"):
                    print(f"[PAYROLL SCHEDULER] Executed payroll for company {result['company_id']}: {result['total_amount']} USDC")
    except Exception as e:
        print(f"[PAYROLL SCHEDULER] Error: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Start scheduler
    # Check every minute for payroll time
    scheduler.add_job(
        run_payroll_check,
        trigger=CronTrigger(second=0),  # Run at the start of every minute
        id="payroll_check",
        replace_existing=True
    )
    scheduler.start()
    print("[APP] Payroll scheduler started - checking every minute")
    
    yield
    
    # Shutdown: Stop scheduler
    scheduler.shutdown()
    print("[APP] Payroll scheduler stopped")


app = FastAPI(title="BossBoard API", version="1.0.0", lifespan=lifespan)

# CORS middleware - support both localhost and ngrok URLs
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8001",
]

# Add ngrok frontend URL from environment variable if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)
    print(f"[CORS] Added frontend URL: {frontend_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(company.router)
app.include_router(departments.router)
app.include_router(workers.router)
app.include_router(spendings.router)
app.include_router(revenue.router)
app.include_router(payroll.router)
app.include_router(dashboard.router)
app.include_router(circle.router)


@app.get("/")
async def root():
    return {"message": "BossBoard API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    # Support Railway and other platforms that set PORT environment variable
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

