# BossBoard Frontend

Modern React + TypeScript frontend for the BossBoard Treasury & Payroll Dashboard.

## Features

- 📊 **Dashboard**: Overview with treasury balance, revenue, payroll, profit, and charts
- 🏢 **Departments**: Create and manage departments
- 👥 **Workers**: Add workers, manage their status, assign to departments
- 💰 **Treasury**: View balance, top up treasury via Circle, transaction history
- 📈 **Analytics**: Visual analytics with charts and key statistics

## Tech Stack

- React 18
- TypeScript
- Vite
- React Router
- Recharts (for data visualization)
- Axios (for API calls)
- date-fns (for date formatting)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional, defaults to `http://localhost:8000/api`):
```env
VITE_API_URL=http://localhost:8000/api
```

3. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## API Endpoints Expected

The frontend expects the following API endpoints from the backend:

- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/treasury/balance` - Treasury balance
- `POST /api/treasury/top-up` - Initiate treasury top-up
- `GET /api/treasury/transactions` - Transaction history
- `GET /api/departments` - List departments
- `POST /api/departments` - Create department
- `GET /api/workers` - List workers
- `POST /api/workers` - Add worker
- `PATCH /api/workers/:id/status` - Update worker status
- `GET /api/analytics` - Analytics data

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── Dashboard.tsx
│   │   ├── Departments.tsx
│   │   ├── Workers.tsx
│   │   ├── Treasury.tsx
│   │   └── Analytics.tsx
│   ├── services/        # API service layer
│   │   └── api.ts
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   ├── App.tsx          # Main app component with routing
│   ├── App.css          # Global styles
│   ├── main.tsx         # Entry point
│   └── index.css        # Base styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

