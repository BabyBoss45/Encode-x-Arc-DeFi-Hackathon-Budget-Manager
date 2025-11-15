# BossBoard Backend API

FastAPI backend with PostgreSQL database and Circle API integration.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create PostgreSQL database:
```bash
createdb bossboard
```

3. Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

4. Update `.env` with:
   - Database connection string
   - JWT secret key
   - Circle API key

5. Run database migrations (if using Alembic):
```bash
alembic upgrade head
```

Or tables will be created automatically on first run.

6. Start the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/company/` - Get company info
- `PUT /api/company/master-wallet` - Set master wallet
- `GET /api/departments/` - Get all departments
- `POST /api/departments/` - Create department
- `GET /api/workers/` - Get all workers
- `POST /api/workers/` - Create worker
- `GET /api/spendings/` - Get all spendings
- `POST /api/spendings/` - Create spending
- `GET /api/revenue/` - Get all revenues
- `POST /api/revenue/` - Create revenue
- `POST /api/payroll/execute` - Execute payroll
- `GET /api/dashboard/stats` - Get dashboard statistics

## Authentication

Most endpoints require JWT authentication. Include token in header:
```
Authorization: Bearer <token>
```

