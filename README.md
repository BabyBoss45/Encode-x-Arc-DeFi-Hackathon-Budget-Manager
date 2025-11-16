# BossBoard - Budget Manager & Payroll System

A comprehensive budget management and automated payroll system with Circle API integration for USDC payments.

## 🚀 Features

- **Company Management**: Create and manage company profiles
- **Department Management**: Organize workers into departments
- **Worker Management**: Add workers with wallet addresses and salaries
- **Automated Payroll**: Schedule and automatically execute USDC payroll payments via Circle API
- **Revenue Tracking**: Track monthly revenue
- **Spending Management**: Track additional company spendings
- **Dashboard Analytics**: View statistics, charts, and treasury balance
- **Circle Wallet Integration**: Manage USDC wallets and view balances

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - Runs on `localhost:8000`
- **Frontend**: React + TypeScript + Vite - Runs on `localhost:3000`
- **Database**: PostgreSQL via ngrok tunnel
- **Payments**: Circle Developer-Controlled Wallets API

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **PostgreSQL 12+**
- **ngrok** (for database tunnel)
- **Circle API Account** (for USDC payments)

## 🔧 Installation & Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Encode-x-Arc-DeFi-Hackathon-Budget-Manager
```

### 2. Database Setup

#### Install PostgreSQL

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Install and remember the password for `postgres` user
- Default port: `5432`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@14
```

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE bossboard;

# Exit
\q
```

#### Create Tables

```bash
cd backend
psql -U postgres -d bossboard -f postgresql_schema.sql
```

#### Configure PostgreSQL for External Access

1. Edit `postgresql.conf` (usually in `C:\Program Files\PostgreSQL\14\data\`):
   ```
   listen_addresses = '*'
   ```

2. Edit `pg_hba.conf` (same directory):
   ```
   host    all             all             0.0.0.0/0               md5
   ```

3. Restart PostgreSQL service

### 3. Setup ngrok for Database

#### Install ngrok

1. Download from https://ngrok.com/download
2. Extract `ngrok.exe` to a folder in your PATH
3. Or add ngrok location to PATH environment variable

#### Start ngrok Tunnel

```powershell
ngrok tcp 5432
```

**Keep this window open!** The tunnel must stay active.

Copy the ngrok URL (e.g., `tcp://2.tcp.eu.ngrok.io:14007`)

### 4. Backend Setup

#### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables

Create `backend/.env` file:

```env
# Database (PostgreSQL via ngrok)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@NGROK_HOST:NGROK_PORT/bossboard

# Example:
# DATABASE_URL=postgresql://postgres:admin@2.tcp.eu.ngrok.io:14007/bossboard

# JWT Secret Key (minimum 32 characters)
JWT_SECRET_KEY=your-secret-key-change-in-production-min-32-chars

# Circle API Configuration
CIRCLE_API_KEY=TEST_API_KEY:your_key_id:your_key_secret
ENTITY_SECRET=your_64_character_hex_entity_secret
USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

**Get Circle API Credentials:**
1. Sign up at https://developers.circle.com
2. Create API Key → Copy `TEST_API_KEY:key_id:key_secret`
3. Get Entity Secret from Developer Settings (64 hex characters)

#### Test Database Connection

```bash
cd backend
python check_connection.py
```

Should show: `[OK] Connection successful!`

#### Start Backend Server

```bash
cd backend
python main.py
```

Backend will run on: `http://localhost:8000`

### 5. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure API URL

Create `frontend/.env` file (optional, defaults to `http://localhost:8000/api`):

```env
VITE_API_URL=http://localhost:8000/api
```

#### Start Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:3000`

## 🎯 Usage

### Access the Application

1. Open browser: `http://localhost:3000`
2. Register a new account or login
3. Set up your company wallet address
4. Create departments and add workers
5. Schedule payroll payments
6. Track revenue and spending

### API Endpoints

**Base URL**: `http://localhost:8000/api`

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

**Company:**
- `GET /api/company/` - Get company info
- `PUT /api/company/master-wallet` - Set master wallet

**Departments:**
- `GET /api/departments/` - Get all departments
- `POST /api/departments/` - Create department

**Workers:**
- `GET /api/workers/` - Get all workers
- `POST /api/workers/` - Add worker
- `PATCH /api/workers/{id}/status` - Update worker status

**Payroll:**
- `POST /api/payroll/execute` - Execute payroll manually
- `GET /api/payroll/transactions` - Get payroll history

**Dashboard:**
- `GET /api/dashboard/stats` - Get dashboard statistics

**Circle Wallet:**
- `GET /api/circle/wallet/info` - Get wallet information
- `GET /api/circle/wallet/balance` - Get USDC balance

See `TECHNICAL.md` for complete API documentation.

## ⚠️ Important Notes

### Database ngrok Tunnel

- **Keep ngrok running** - If you close the ngrok window, database connection will break
- **URL changes** - If ngrok restarts, you'll get a new URL
- **Update DATABASE_URL** in `backend/.env` if ngrok URL changes

### Automated Payroll

- Payroll scheduler runs every minute
- Checks for scheduled payroll times
- Automatically executes payments via Circle API
- Transactions are saved to database

### Environment Variables

- Never commit `.env` files to git
- Keep `ENTITY_SECRET` secure (64 hex characters)
- Use different `JWT_SECRET_KEY` in production

## 🐛 Troubleshooting

### Database Connection Failed

1. Check PostgreSQL is running: `netstat -ano | findstr :5432`
2. Verify ngrok tunnel is active (check ngrok window)
3. Update `DATABASE_URL` in `.env` if ngrok restarted
4. Test connection: `python backend/check_connection.py`

### Backend Not Starting

1. Check all dependencies installed: `pip install -r requirements.txt`
2. Verify `.env` file exists and has correct values
3. Check port 8000 is not in use: `netstat -ano | findstr :8000`
4. Review error logs in terminal

### Frontend Can't Connect to Backend

1. Verify backend is running on `http://localhost:8000`
2. Check `VITE_API_URL` in `frontend/.env`
3. Check browser console (F12) for CORS errors
4. Verify `FRONTEND_URL` in backend `.env` matches frontend URL

### Circle API Errors

1. Verify `CIRCLE_API_KEY` format: `TEST_API_KEY:key_id:key_secret`
2. Check `ENTITY_SECRET` is exactly 64 hex characters
3. Verify wallet is created and funded
4. Check Circle API logs in backend terminal

## 📁 Project Structure

```
.
├── backend/
│   ├── src/
│   │   ├── routes/          # API route handlers
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # Database connection
│   │   ├── auth.py          # Authentication utilities
│   │   ├── circle_api.py    # Circle API client
│   │   └── payroll_scheduler.py  # Automated payroll
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── postgresql_schema.sql # Database schema
│   └── .env                 # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service layer
│   │   └── types/           # TypeScript types
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
│
└── README.md                # This file
```

## 🔐 Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Entity secrets encrypted before storage
- CORS configured for frontend domain
- Environment variables for sensitive data

## 📚 Additional Documentation

- **TECHNICAL.md** - Complete technical documentation
- **backend/CIRCLE_INTEGRATION.md** - Circle API integration details
- **backend/POSTGRESQL_SETUP.md** - PostgreSQL setup reference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

[Your License Here]

## 👥 Authors

[Your Name/Team]

---

**Need Help?** Check `TECHNICAL.md` for detailed API documentation and technical details.

