#!/usr/bin/env python3
"""
Simple script to run the frontend
Just run this file: python run_frontend.py
"""
import sys
import os
import subprocess

# Change to src directory
os.chdir(os.path.join(os.path.dirname(__file__), 'src'))

# Check dependencies
try:
    import fastapi
    import uvicorn
    import jinja2
except ImportError:
    print("❌ Dependencies not installed!")
    print("\n📦 Install them with:")
    print("   pip3 install fastapi uvicorn jinja2 python-multipart")
    print("\nOr:")
    print("   python3 -m pip install fastapi uvicorn jinja2 python-multipart")
    print("\nOr:")
    print("   pip3 install -r requirements_frontend.txt")
    sys.exit(1)

# Run frontend
print("🚀 Starting BossBoard Frontend...")
print("📝 Open in browser: http://localhost:8001/login")
print("⏹️  Press Ctrl+C to stop\n")

try:
    import uvicorn
    uvicorn.run("frontend:app", host="0.0.0.0", port=8001, reload=True)
except KeyboardInterrupt:
    print("\n👋 Stopping server...")
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

