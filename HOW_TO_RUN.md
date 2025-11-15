# 🚀 How to Run Frontend - SIMPLE INSTRUCTIONS

## Option 1: Easiest (Recommended)

### Step 1: Install Dependencies
Open terminal in the project folder and run:

```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### Step 2: Run the Script
In the same folder, run:

```bash
python run_frontend.py
```

Done! Open browser: **http://localhost:8001/login**

---

## Option 2: Manual

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### Step 2: Navigate to src folder
```bash
cd src
```

### Step 3: Run frontend.py
```bash
python frontend.py
```

Or via uvicorn:
```bash
uvicorn frontend:app --host 0.0.0.0 --port 8001 --reload
```

---

## 📁 Which file to open?

**You DON'T need to open files in an editor to run them!**

Just run in terminal:
- `python run_frontend.py` (from project root folder)
- OR `python src/frontend.py` (from project root folder)
- OR `cd src && python frontend.py` (from project root folder)

---

## 🌐 What to do after running?

1. Open browser (Chrome, Firefox, Safari - any)
2. Enter address: **http://localhost:8001/login**
3. You will see the login page!

---

## ✅ Check that it works:

1. Open: http://localhost:8001/signup
2. Register (e.g., email: `test@example.com`, password: `123`)
3. Open: http://localhost:8001/login
4. Login with your credentials
5. You will be redirected to Dashboard!

---

## ❌ If it doesn't work:

### Error "ModuleNotFoundError"
Install dependencies:
```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### Error "Address already in use"
Port 8001 is in use. Change port in `src/frontend.py` (last line):
```python
uvicorn.run(app, host="0.0.0.0", port=8002)  # Change to 8002
```

### Don't know how to open terminal?
- **Mac**: Press Cmd+Space, type "Terminal"
- **Windows**: Press Win+R, type "cmd" or "powershell"
- **Linux**: Ctrl+Alt+T

---

## 📝 What's next?

After Login and Sign Up work, we will add:
- Dashboard with balance and statistics
- Departments page
- Workers page
- Treasury page
- Analytics page

