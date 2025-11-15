# ✅ Frontend Integration with Backend API

## Problem solved!

Frontend is now connected to Backend API. Data is saved in the database and won't be lost on restart!

## How it works:

### 1. **Automatic Backend Detection**
- Frontend checks backend availability on each request
- If backend is available → uses API (data in DB)
- If backend is unavailable → uses fallback (in-memory, for testing only)

### 2. **Authentication via JWT**
- On registration/login, JWT token is received
- Token is saved in cookie
- All API requests use token for authorization

### 3. **Data Persistence**
- All data is saved to PostgreSQL/SQLite via API
- Data is linked to user (company_id)
- Data won't be lost on restart

## How to run:

### Step 1: Run Backend

```bash
cd backend
python3 main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Run Frontend

In a **NEW** terminal:

```bash
cd src
python3 frontend.py
```

You should see:
```
🚀 Starting ARC budget frontend on http://localhost:8001
💡 Make sure backend is running on http://localhost:8000 for data persistence
```

### Step 3: Open in Browser

**http://localhost:8001/login**

## What changed:

✅ **Registration** → saved to DB via API  
✅ **Login** → verification via API, JWT token received  
✅ **Creating departments** → saved to DB  
✅ **Adding workers** → saved to DB  
✅ **Adding spendings** → saved to DB  
✅ **Adding revenues** → saved to DB  
✅ **Dashboard** → data from DB via API  

## Important:

- **Backend must be running** to save data
- If backend is not running, frontend will work in fallback mode (data lost on restart)
- JWT token is stored in cookie and automatically used for all requests

## Check that it works:

1. Register
2. Create a department
3. Add a worker
4. Restart frontend
5. Login again → **data should be saved!** ✅

Now data won't be lost! 🎉

