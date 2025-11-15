# Complete Setup Guide

## Project Structure

```
Encode-x-Arc-DeFi-Hackathon/
├── backend/              # FastAPI backend with PostgreSQL
│   ├── main.py          # API entry point
│   ├── src/
│   │   ├── database.py  # DB connection
│   │   ├── models.py    # SQLAlchemy models
│   │   ├── auth.py      # JWT authentication
│   │   ├── circle_api.py # Circle API client
│   │   └── routes/      # API endpoints
│   └── requirements.txt
├── src/                  # Python frontend (templates)
│   ├── frontend.py      # Main frontend app
│   ├── api_client.py    # API client for backend
│   ├── templates/       # HTML templates
│   └── static/          # CSS files
└── frontend/            # React frontend (optional)
```

## Quick Start

### Step 1: Setup Database

```bash
# Create PostgreSQL database
createdb bossboard

# Or using Docker:
docker run --name bossboard-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=bossboard -p 5432:5432 -d postgres
```

### Step 2: Setup Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost/bossboard
JWT_SECRET_KEY=your-secret-key-change-this
CIRCLE_API_KEY=your-circle-api-key
CIRCLE_BASE_URL=https://api.circle.com/v1
EOF

# Start backend (runs on port 8000)
python main.py
```

### Step 3: Setup Frontend

```bash
# Option A: Use existing Python frontend
cd src
pip install fastapi uvicorn jinja2 python-multipart requests

# Set API URL (optional, defaults to http://localhost:8000/api)
export API_BASE_URL=http://localhost:8000/api

# Start frontend (runs on port 8001)
python frontend.py
```

### Step 4: Access Application

- Frontend: http://localhost:8001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Integration Status

✅ Backend API created with:
- PostgreSQL database models
- JWT authentication
- Circle API integration
- All CRUD endpoints
- Payroll execution
- Dashboard statistics

✅ Frontend structure:
- Login/Register pages
- Constructor page with block visualization
- Dashboard page
- API client for backend integration

## Next Steps to Complete Integration

1. **Update frontend.py to use API client**:
   - Replace in-memory storage with API calls
   - Add JWT token management (store in session/cookie)
   - Update all forms to use API endpoints

2. **Add session management**:
   - Store JWT token after login
   - Include token in all API requests
   - Handle token expiration

3. **Test Circle API integration**:
   - Get Circle API key
   - Test wallet creation
   - Test payment transfers

4. **Deploy**:
   - Setup production database
   - Configure environment variables
   - Deploy backend and frontend

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/bossboard
JWT_SECRET_KEY=your-secret-key
CIRCLE_API_KEY=your-circle-api-key
CIRCLE_BASE_URL=https://api.circle.com/v1
```

### Frontend (optional)
```
API_BASE_URL=http://localhost:8000/api
```

## API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

