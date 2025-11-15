"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routes import auth, company, departments, workers, spendings, revenue, payroll, dashboard

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BossBoard API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8001"],  # Frontend URLs
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


@app.get("/")
async def root():
    return {"message": "BossBoard API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

