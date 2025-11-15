# ⚡ Quick Start (WITHOUT PostgreSQL)

## Easiest way - use SQLite

SQLite is a built-in database, no installation required!

## Step 1: Install Dependencies

```bash
# Backend dependencies
cd backend
pip3 install -r requirements.txt

# Frontend dependencies (if not installed yet)
cd ../src
pip3 install fastapi uvicorn jinja2 python-multipart requests
```

## Step 2: Create .env file for backend

```bash
cd backend
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./bossboard.db
JWT_SECRET_KEY=my-secret-key-change-in-production
CIRCLE_API_KEY=test-key
CIRCLE_BASE_URL=https://api.circle.com/v1
EOF
```

**Note**: SQLite doesn't require DATABASE_URL setup - it will create `bossboard.db` file automatically!

## Step 3: Run Backend

```bash
cd backend
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

## Step 4: Run Frontend (in NEW terminal)

Open a new terminal:

```bash
cd src
python3 frontend.py
```

You should see:
```
🚀 Starting frontend on http://localhost:8001
```

## Step 5: Open in Browser

Open: **http://localhost:8001/login**

## Done! 🎉

Now you can:
1. Register
2. Login to the system
3. Use the constructor

## What's happening:

- **Backend** (port 8000) - processes requests, saves to database
- **Frontend** (port 8001) - shows pages, sends requests to backend
- **Database** - file `bossboard.db` in `backend/` folder (created automatically)

## If you need PostgreSQL (later):

1. Install PostgreSQL
2. Create database: `createdb bossboard`
3. Change in `.env`: `DATABASE_URL=postgresql://postgres:password@localhost/bossboard`

But for now SQLite is enough!

