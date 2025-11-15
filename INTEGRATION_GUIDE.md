# Integration Guide: Block-Based Business Management System

## Architecture Overview

- **Backend API**: FastAPI with PostgreSQL (runs on port 8000)
- **Frontend**: Python FastAPI with templates (runs on port 8001) OR React frontend
- **Database**: PostgreSQL
- **Payments**: Circle API integration

## Setup Instructions

### 1. Database Setup

```bash
# Install PostgreSQL if not installed
# Create database
createdb bossboard

# Or using psql:
psql -U postgres
CREATE DATABASE bossboard;
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your settings:
# DATABASE_URL=postgresql://user:password@localhost/bossboard
# JWT_SECRET_KEY=your-secret-key
# CIRCLE_API_KEY=your-circle-api-key

# Run backend
python main.py
# Or: uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

### 3. Frontend Setup (Python version)

The existing `src/frontend.py` can be updated to use the new API, or you can keep it as a simple template-based frontend.

### 4. Frontend Setup (React version - Optional)

If you want to use React frontend:

```bash
cd frontend
npm install
npm run dev
```

React frontend will be at: `http://localhost:3000`

## API Endpoints

All endpoints are prefixed with `/api/`

### Authentication
- `POST /api/auth/register` - Register
- `POST /api/auth/login` - Login (returns JWT token)

### Company
- `GET /api/company/` - Get company info
- `PUT /api/company/master-wallet` - Set master wallet

### Departments
- `GET /api/departments/` - List departments
- `POST /api/departments/` - Create department
- `DELETE /api/departments/{id}` - Delete department

### Workers
- `GET /api/workers/` - List workers
- `POST /api/workers/` - Create worker
- `PUT /api/workers/{id}` - Update worker
- `DELETE /api/workers/{id}` - Delete worker

### Spendings
- `GET /api/spendings/` - List spendings
- `POST /api/spendings/` - Create spending
- `DELETE /api/spendings/{id}` - Delete spending

### Revenue
- `GET /api/revenue/` - List revenues
- `POST /api/revenue/` - Create revenue

### Payroll
- `POST /api/payroll/execute` - Execute payroll
- `GET /api/payroll/transactions` - Get payroll transactions

### Dashboard
- `GET /api/dashboard/stats` - Get statistics

## Authentication

Most endpoints require JWT token in header:
```
Authorization: Bearer <token>
```

## Next Steps

1. Update `src/frontend.py` to call backend API instead of using in-memory storage
2. Add JWT token storage and management
3. Update forms to use API endpoints
4. Add error handling for API calls

