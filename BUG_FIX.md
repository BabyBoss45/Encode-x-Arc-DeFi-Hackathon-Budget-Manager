# 🔧 Fixing Error "command not found: pip"

On Mac, you often need to use `pip3` instead of `pip`.

## Solution 1: Use pip3 (easiest)

Instead of:
```bash
pip install fastapi uvicorn jinja2 python-multipart
```

Try:
```bash
pip3 install fastapi uvicorn jinja2 python-multipart
```

---

## Solution 2: Use python3 -m pip

```bash
python3 -m pip install fastapi uvicorn jinja2 python-multipart
```

---

## Solution 3: Check if Python is installed

Check Python version:
```bash
python3 --version
```

If Python is not installed, install it:
```bash
brew install python3
```

Or download from official site: https://www.python.org/downloads/

---

## Solution 4: Use virtual environment (recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Now pip will work
pip install fastapi uvicorn jinja2 python-multipart
```

---

## After installing dependencies:

Run frontend:
```bash
python3 run_frontend.py
```

Or:
```bash
python3 src/frontend.py
```
