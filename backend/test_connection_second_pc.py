#!/usr/bin/env python3
"""
Скрипт для проверки подключения на втором ПК
"""
import sys
import os

print("=" * 80)
print("CHECKING SETUP FOR SECOND PC")
print("=" * 80)

# 1. Check Python version
print("\n[1] Checking Python version...")
try:
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  [WARNING] Python 3.8+ required!")
    else:
        print("  [OK] Python version OK")
except Exception as e:
    print(f"  [ERROR] {e}")

# 2. Check .env file
print("\n[2] Checking .env file...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"  [OK] .env file exists at: {env_path}")
    with open(env_path, 'r') as f:
        content = f.read()
        if 'DATABASE_URL' in content:
            if 'ngrok' in content or 'localhost' in content:
                print("  [OK] DATABASE_URL found")
            else:
                print("  [WARNING] DATABASE_URL might be incorrect")
        else:
            print("  [ERROR] DATABASE_URL not found in .env")
else:
    print(f"  [ERROR] .env file not found at: {env_path}")
    print("  Create it with:")
    print("    DATABASE_URL=postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard")

# 3. Check required packages
print("\n[3] Checking required packages...")
required_packages = [
    'psycopg2',
    'fastapi',
    'uvicorn',
    'sqlalchemy',
    'python-dotenv',
    'pydantic',
    'passlib',
    'python-jose',
    'jinja2',
    'requests'
]

missing = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"  [OK] {package}")
    except ImportError:
        print(f"  [MISSING] {package}")
        missing.append(package)

if missing:
    print(f"\n  Install missing packages:")
    print(f"    pip install {' '.join(missing)}")

# 4. Test database connection
print("\n[4] Testing database connection...")
try:
    from dotenv import load_dotenv
    import psycopg2
    
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("  [ERROR] DATABASE_URL not set in .env")
    elif not DATABASE_URL.startswith("postgresql"):
        print(f"  [ERROR] Invalid DATABASE_URL format: {DATABASE_URL[:50]}...")
    else:
        print(f"  Connecting to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'unknown'}...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check connection
        cursor.execute("SELECT current_database(), version()")
        db_info = cursor.fetchone()
        print(f"  [OK] Connected to database: {db_info[0]}")
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"  [OK] Users in database: {user_count}")
        
        if user_count == 0:
            print("  [WARNING] Database is empty!")
        else:
            print("  [OK] Database has data")
        
        conn.close()
        
except ImportError as e:
    print(f"  [ERROR] Missing package: {e}")
    print("  Install: pip install psycopg2-binary python-dotenv")
except Exception as e:
    print(f"  [ERROR] Connection failed: {e}")
    print("  Check:")
    print("    1. Ngrok running on first PC?")
    print("    2. Correct address in .env?")
    print("    3. Internet connection?")

# 5. Check ports
print("\n[5] Checking ports...")
try:
    import socket
    
    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    
    ports = {8000: 'Backend', 8001: 'Frontend'}
    for port, name in ports.items():
        if check_port(port):
            print(f"  [WARNING] Port {port} ({name}) is already in use")
        else:
            print(f"  [OK] Port {port} ({name}) is free")
            
except Exception as e:
    print(f"  [WARNING] Could not check ports: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if missing:
    print("\n[ACTION REQUIRED] Install missing packages:")
    print(f"  pip install {' '.join(missing)}")
else:
    print("\n[OK] All packages installed")

print("\nNext steps:")
print("  1. Make sure ngrok is running on first PC")
print("  2. Update .env with correct ngrok address")
print("  3. Run: cd backend && python main.py")
print("  4. Run: python run_frontend.py (in another terminal)")

