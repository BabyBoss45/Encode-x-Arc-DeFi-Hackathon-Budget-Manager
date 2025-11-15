#!/bin/bash
# Script to run frontend

echo "🚀 Starting BossBoard Frontend..."

cd src

# Check dependencies
echo "📦 Checking dependencies..."
pip3 install -q fastapi uvicorn jinja2 python-multipart requests

# Run frontend
echo "🚀 Starting on http://localhost:8001"
python3 frontend.py
