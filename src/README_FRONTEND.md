# Simple Python Frontend for BossBoard

This is a simple Python frontend using FastAPI. Starting with Login and Sign Up pages.

## How to run:

### 1. Install dependencies:

```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### 2. Run frontend:

```bash
cd src
python frontend.py
```

Or via uvicorn:

```bash
cd src
uvicorn frontend:app --host 0.0.0.0 --port 8001
```

### 3. Open in browser:

```
http://localhost:8001/login
```

## File structure:

```
src/
├── frontend.py          # Main file with FastAPI application
├── templates/           # HTML templates
│   ├── login.html       # Login page
│   ├── signup.html      # Sign up page
│   └── dashboard.html   # Main page (placeholder for now)
└── static/              # CSS and other static files
    └── style.css        # Styles
```

## What already works:

✅ Login page (`/login`)
✅ Sign Up page (`/signup`)
✅ Simple user verification
✅ Beautiful design

## Important:

⚠️ **WARNING**: Currently passwords are stored in memory without encryption! 
In a real project you need to:
- Use a database
- Hash passwords (bcrypt, argon2)
- Use sessions or JWT tokens for authorization

## Next steps:

1. Add database connection
2. Add password hashing
3. Add sessions/tokens
4. Create remaining pages (Dashboard, Departments, Workers, Treasury, Analytics)

## If you encounter problems:

1. Make sure all dependencies are installed
2. Check that port 8001 is free
3. If port is busy, change port in `frontend.py` (line with `uvicorn.run`)
