#!/bin/bash
# Script to run backend

echo "🚀 Starting BossBoard Backend..."

cd backend

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
DATABASE_URL=sqlite:///./bossboard.db
JWT_SECRET_KEY=my-secret-key-change-in-production
CIRCLE_API_KEY=test-key
CIRCLE_BASE_URL=https://api.circle.com/v1
EOF
    echo "✅ .env file created"
fi

# Check dependencies
echo "📦 Checking dependencies..."
pip3 install -q -r requirements.txt

# Run backend
echo "🚀 Starting on http://localhost:8000"
python3 main.py
