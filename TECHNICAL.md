# BossBoard - Technical Documentation

## Architecture Overview

### Technology Stack

**Backend:**
- **Framework**: FastAPI 0.104+
- **Database ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL 12+ (via ngrok tunnel)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Scheduler**: APScheduler (for automated payroll)
- **HTTP Client**: requests
- **Encryption**: cryptography (for Circle entity secrets)

**Frontend:**
- **Framework**: React 18
- **Language**: TypeScript 5.3+
- **Build Tool**: Vite 5.0+
- **Routing**: React Router DOM 6.20+
- **HTTP Client**: Axios 1.6+
- **Charts**: Recharts 2.10+
- **Date Utils**: date-fns 2.30+

**External Services:**
- **Circle API**: Developer-Controlled Wallets REST API
- **Blockchain**: ARC-TESTNET (for USDC)
- **Tunnel**: ngrok (for database access)

## Database Schema

### Tables

**users**
- `id` (SERIAL PRIMARY KEY)
- `email` (VARCHAR UNIQUE)
- `password_hash` (VARCHAR)
- `company_name` (VARCHAR)
- `created_at` (TIMESTAMP)

**companies**
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER UNIQUE, FK → users.id)
- `master_wallet_address` (VARCHAR) - Blockchain address
- `circle_wallet_id` (VARCHAR) - Circle wallet UUID
- `circle_wallet_set_id` (VARCHAR) - Circle wallet set UUID
- `entity_secret_encrypted` (VARCHAR) - Encrypted entity secret
- `payroll_date` (DATE) - Scheduled payroll date
- `payroll_time` (VARCHAR) - Scheduled payroll time (HH:MM)
- `created_at` (TIMESTAMP)

**departments**
- `id` (SERIAL PRIMARY KEY)
- `company_id` (INTEGER, FK → companies.id)
- `name` (VARCHAR)
- `created_at` (TIMESTAMP)

**workers**
- `id` (SERIAL PRIMARY KEY)
- `department_id` (INTEGER, FK → departments.id)
- `name` (VARCHAR)
- `surname` (VARCHAR)
- `salary` (DOUBLE PRECISION)
- `wallet_address` (VARCHAR) - Recipient wallet address
- `is_active` (BOOLEAN)
- `created_at` (TIMESTAMP)

**revenues**
- `id` (SERIAL PRIMARY KEY)
- `company_id` (INTEGER, FK → companies.id)
- `amount` (DOUBLE PRECISION)
- `month` (INTEGER, 1-12)
- `year` (INTEGER)
- `created_at` (TIMESTAMP)

**additional_spendings**
- `id` (SERIAL PRIMARY KEY)
- `company_id` (INTEGER, FK → companies.id)
- `department_id` (INTEGER, FK → departments.id, nullable)
- `name` (VARCHAR)
- `amount` (DOUBLE PRECISION)
- `wallet_address` (VARCHAR)
- `created_at` (TIMESTAMP)

**payroll_transactions**
- `id` (SERIAL PRIMARY KEY)
- `company_id` (INTEGER, FK → companies.id)
- `worker_id` (INTEGER, FK → workers.id)
- `amount` (DOUBLE PRECISION)
- `period_start` (DATE)
- `period_end` (DATE)
- `status` (VARCHAR) - pending, completed, failed, INITIATED, QUEUED, SENT, CONFIRMED, COMPLETE
- `transaction_hash` (VARCHAR) - Blockchain transaction hash
- `circle_transaction_id` (VARCHAR) - Circle transaction UUID
- `created_at` (TIMESTAMP)

**spending_transactions**
- `id` (SERIAL PRIMARY KEY)
- `spending_id` (INTEGER, FK → additional_spendings.id)
- `amount` (DOUBLE PRECISION)
- `transaction_hash` (VARCHAR)
- `status` (VARCHAR) - pending, completed, failed
- `created_at` (TIMESTAMP)

## API Endpoints

### Authentication

**POST** `/api/auth/register`
- Register a new user
- **Body**: `{ "email": string, "password": string, "company_name": string }`
- **Response**: `{ "access_token": string, "token_type": "bearer" }`

**POST** `/api/auth/login`
- Login user
- **Body**: `{ "email": string, "password": string }`
- **Response**: `{ "access_token": string, "token_type": "bearer" }`

**Headers**: `Authorization: Bearer <token>`

### Company

**GET** `/api/company/`
- Get company information
- **Auth**: Required
- **Response**: Company object with wallet info

**PUT** `/api/company/master-wallet`
- Set master wallet address
- **Auth**: Required
- **Body**: `{ "master_wallet_address": string }`

### Departments

**GET** `/api/departments/`
- Get all departments for user's company
- **Auth**: Required
- **Response**: Array of department objects

**POST** `/api/departments/`
- Create new department
- **Auth**: Required
- **Body**: `{ "name": string }`
- **Response**: Created department object

**PUT** `/api/departments/{id}`
- Update department
- **Auth**: Required
- **Body**: `{ "name": string }`

**DELETE** `/api/departments/{id}`
- Delete department
- **Auth**: Required

### Workers

**GET** `/api/workers/`
- Get all workers (optionally filtered by department)
- **Auth**: Required
- **Query**: `?department_id=<id>` (optional)
- **Response**: Array of worker objects

**POST** `/api/workers/`
- Add new worker
- **Auth**: Required
- **Body**: `{ "name": string, "surname": string, "department_id": int, "salary": float, "wallet_address": string }`
- **Response**: Created worker object

**PATCH** `/api/workers/{id}/status`
- Update worker active status
- **Auth**: Required
- **Body**: `{ "active": boolean }`

### Payroll

**POST** `/api/payroll/execute`
- Execute payroll manually
- **Auth**: Required
- **Body**: `{ "period_start": "YYYY-MM-DD", "period_end": "YYYY-MM-DD" }`
- **Response**: Payroll execution result

**GET** `/api/payroll/transactions`
- Get payroll transaction history
- **Auth**: Required
- **Response**: Array of transaction objects

**POST** `/api/payroll/schedule`
- Schedule payroll time
- **Auth**: Required
- **Body**: `{ "payroll_date": "YYYY-MM-DD", "payroll_time": "HH:MM" }`

### Revenue

**GET** `/api/revenue/`
- Get all revenue records
- **Auth**: Required
- **Response**: Array of revenue objects

**POST** `/api/revenue/`
- Create revenue record
- **Auth**: Required
- **Body**: `{ "amount": float, "month": int, "year": int }`
- **Response**: Created revenue object

### Spendings

**GET** `/api/spendings/`
- Get all spending records
- **Auth**: Required
- **Query**: `?department_id=<id>` (optional)
- **Response**: Array of spending objects

**POST** `/api/spendings/`
- Create spending record
- **Auth**: Required
- **Body**: `{ "name": string, "amount": float, "wallet_address": string, "department_id": int (optional) }`
- **Response**: Created spending object

### Dashboard

**GET** `/api/dashboard/stats`
- Get dashboard statistics
- **Auth**: Required
- **Response**: 
  ```json
  {
    "totalWorkers": int,
    "totalDepartments": int,
    "totalPayroll": float,
    "totalRevenue": float,
    "totalSpending": float,
    "profit": float,
    "treasuryBalance": float
  }
  ```

### Circle Wallet

**GET** `/api/circle/wallet/info`
- Get wallet information
- **Auth**: Required
- **Response**: Wallet info with addresses

**GET** `/api/circle/wallet/balance`
- Get USDC balance
- **Auth**: Required
- **Response**: `{ "balance": float, "balanceFormatted": string }`

**GET** `/api/circle/wallet/all-balances`
- Get all token balances
- **Auth**: Required
- **Response**: Array of balance objects

## Circle API Integration

### Wallet Management

The system uses Circle Developer-Controlled Wallets API:

1. **Wallet Creation**: Automatically creates wallet when master wallet is set
2. **Entity Secret**: Encrypted and stored in database
3. **USDC Transfers**: Automated payroll payments via Circle API
4. **Balance Tracking**: Real-time USDC balance from Circle API

### Payment Flow

1. User schedules payroll time
2. Scheduler checks every minute
3. When time matches, system:
   - Fetches all active workers
   - Calculates total amount needed
   - Checks wallet balance
   - Creates Circle transfer transactions
   - Updates transaction status
   - Saves to database

### Transaction Statuses

- `INITIATED` - Transaction created
- `QUEUED` - Waiting in queue
- `SENT` - Sent to blockchain
- `CONFIRMED` - Confirmed on blockchain
- `COMPLETE` - Fully completed
- `failed` - Transaction failed

## Security

### Authentication

- **JWT Tokens**: 30-minute expiration
- **Password Hashing**: bcrypt with 12 rounds
- **Token Storage**: Frontend stores in memory/localStorage

### Data Protection

- **Entity Secrets**: Encrypted using RSA public key from Circle
- **Database**: PostgreSQL with connection pooling
- **CORS**: Configured for frontend domain only
- **Environment Variables**: Sensitive data in `.env` files

### Best Practices

- Never commit `.env` files
- Use strong JWT secret keys (32+ characters)
- Keep entity secrets secure (64 hex characters)
- Use HTTPS in production
- Validate all user inputs

## Performance Optimizations

### Database

- **Connection Pooling**: 10 connections, max 20 overflow
- **Indexes**: On foreign keys and frequently queried fields
- **Query Optimization**: Single queries with joins instead of N+1 queries
- **Caching**: Dashboard stats cached for 5 minutes

### API

- **Response Caching**: Dashboard stats cached
- **Batch Operations**: Multiple workers processed in single transaction
- **Async Operations**: Non-blocking I/O for Circle API calls

## Automated Payroll Scheduler

### How It Works

1. **Scheduler**: APScheduler runs every minute (at :00 seconds)
2. **Check**: Queries companies with scheduled payroll time
3. **Match**: Compares current time with scheduled time
4. **Execute**: If match, runs payroll for that company
5. **Log**: Records results in console and database

### Configuration

- **Check Interval**: Every minute
- **Time Format**: 24-hour (HH:MM)
- **Timezone**: Server local time
- **Execution**: Synchronous (one company at a time)

## Error Handling

### Database Errors

- Connection errors retry with exponential backoff
- Transaction rollback on errors
- Detailed error logging

### Circle API Errors

- API errors logged with full details
- Transaction status set to "failed"
- User-friendly error messages

### Validation

- Pydantic schemas validate all inputs
- SQLAlchemy validates database constraints
- Frontend validates before API calls

## Development

### Running Tests

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

### Code Style

- **Backend**: Follow PEP 8
- **Frontend**: ESLint + Prettier
- **Type Hints**: Use type hints in Python
- **TypeScript**: Strict mode enabled

## Deployment Notes

### Environment Variables

Required for backend:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing key
- `CIRCLE_API_KEY` - Circle API credentials
- `ENTITY_SECRET` - Circle entity secret (64 hex)
- `USDC_TOKEN_ID` - USDC token ID (optional)
- `FRONTEND_URL` - Frontend URL for CORS

Required for frontend:
- `VITE_API_URL` - Backend API URL

### Database Migration

Tables are created automatically on first run via:
```python
Base.metadata.create_all(bind=engine)
```

For production, consider using Alembic for migrations.

## Monitoring & Logging

### Backend Logs

- Startup logs: Server start, scheduler start
- Payroll logs: Execution results, errors
- API logs: Request/response (if enabled)
- Error logs: Full stack traces

### Frontend Logs

- Console logs for debugging
- Error boundaries for React errors
- Network logs in browser DevTools

## Future Improvements

- [ ] Database migrations with Alembic
- [ ] Unit and integration tests
- [ ] API rate limiting
- [ ] WebSocket for real-time updates
- [ ] Multi-currency support
- [ ] Advanced analytics and reporting
- [ ] Email notifications
- [ ] Mobile app support

---

For setup instructions, see `README.md`.

