# 🚀 Simple Setup Instructions

## What is PostgreSQL?

PostgreSQL is a database (data storage). We need it to save information about users, workers, departments, etc.

## Option 1: Install PostgreSQL (if not installed)

### On Mac:
```bash
# Install via Homebrew
brew install postgresql@14

# Start PostgreSQL
brew services start postgresql@14
```

### On Windows:
1. Download from official site: https://www.postgresql.org/download/windows/
2. Install (use default settings)
3. Remember password for user `postgres`

### On Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Option 2: Use SQLite (easier, no PostgreSQL installation)

If you don't want to install PostgreSQL, you can use SQLite (built-in database).

## Creating Database

### If using PostgreSQL:

```bash
# Create database
createdb bossboard

# Or via psql:
psql -U postgres
CREATE DATABASE bossboard;
\q
```

### If using SQLite (easier):

No need to create anything! SQLite will create the file automatically.

## Step-by-step Setup Instructions

### Step 1: Check that PostgreSQL is installed

```bash
# Check version
psql --version

# If command not found, install PostgreSQL (see above)
```

### Step 2: Create Database

```bash
createdb bossboard
```

If it says "command not found", try:
```bash
# On Mac/Linux
/usr/local/bin/createdb bossboard

# Or via psql
psql -U postgres -c "CREATE DATABASE bossboard;"
```

### Step 3: Setup Backend

```bash
# Navigate to backend folder
cd backend

# Install dependencies
pip3 install -r requirements.txt
```

### Step 4: Create .env file

```bash
cd backend
cat > .env << 'EOF'
DATABASE_URL=postgresql://postgres:password@localhost/bossboard
JWT_SECRET_KEY=my-secret-key-12345
CIRCLE_API_KEY=your-circle-api-key-here
CIRCLE_BASE_URL=https://api.circle.com/v1
EOF
```

**IMPORTANT**: Replace:
- `password` with your PostgreSQL password (if installed)
- `your-circle-api-key-here` with your real Circle API key (can leave as is for testing)

### Step 5: Run Backend

```bash
cd backend
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Run Frontend (in new terminal)

```bash
cd src
python3 frontend.py
```

You should see:
```
🚀 Starting frontend on http://localhost:8001
```

### Step 7: Open in browser

Open: **http://localhost:8001/login**

## If PostgreSQL doesn't work

### Option A: Use SQLite (easier)

Change in `backend/src/database.py`:

```python
# Was:
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/bossboard")

# Now:
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bossboard.db")
```

And in `backend/src/models.py` add at the beginning:
```python
from sqlalchemy import create_engine
# For SQLite need to add check_same_thread=False
```

### Option B: Use Docker (if Docker is installed)

```bash
# Run PostgreSQL in Docker
docker run --name bossboard-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=bossboard \
  -p 5432:5432 \
  -d postgres

# Now use:
DATABASE_URL=postgresql://postgres:password@localhost/bossboard
```

## Check that everything works

1. Backend works: open http://localhost:8000/docs
2. Frontend works: open http://localhost:8001/login
3. Database works: backend should start without errors

## Common Issues

### Error: "could not connect to server"
- PostgreSQL not running: `brew services start postgresql` (Mac) or `sudo systemctl start postgresql` (Linux)

### Error: "password authentication failed"
- Check password in `.env` file
- Or create user: `createuser -s postgres`

### Error: "database does not exist"
- Create database: `createdb bossboard`

## Quick Start (minimal setup)

If you want to quickly test without PostgreSQL:

1. Use SQLite (see Option A above)
2. Run only frontend (it works without backend, but data won't be saved)

```bash
cd src
python3 frontend.py
```

