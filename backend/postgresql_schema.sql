-- PostgreSQL Schema for BossBoard Budget Manager
-- Run this script to create all tables in PostgreSQL database

-- Enable UUID extension (if needed in future)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Table: companies
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    master_wallet_address VARCHAR(255),
    payroll_date DATE,
    payroll_time VARCHAR(5),  -- Format: HH:MM (24-hour)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_companies_user_id ON companies(user_id);

-- Table: departments
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on company_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_departments_company_id ON departments(company_id);

-- Table: workers
CREATE TABLE IF NOT EXISTS workers (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    salary DOUBLE PRECISION NOT NULL,
    wallet_address VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_workers_department_id ON workers(department_id);
CREATE INDEX IF NOT EXISTS idx_workers_is_active ON workers(is_active);

-- Table: additional_spendings
CREATE TABLE IF NOT EXISTS additional_spendings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    wallet_address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_spendings_company_id ON additional_spendings(company_id);
CREATE INDEX IF NOT EXISTS idx_spendings_department_id ON additional_spendings(department_id);

-- Table: revenues
CREATE TABLE IF NOT EXISTS revenues (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    year INTEGER NOT NULL CHECK (year >= 2000 AND year <= 2100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_revenues_company_id ON revenues(company_id);
CREATE INDEX IF NOT EXISTS idx_revenues_year_month ON revenues(year DESC, month DESC);

-- Table: payroll_transactions
CREATE TABLE IF NOT EXISTS payroll_transactions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    worker_id INTEGER NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    transaction_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_payroll_company_id ON payroll_transactions(company_id);
CREATE INDEX IF NOT EXISTS idx_payroll_worker_id ON payroll_transactions(worker_id);
CREATE INDEX IF NOT EXISTS idx_payroll_status ON payroll_transactions(status);
CREATE INDEX IF NOT EXISTS idx_payroll_period ON payroll_transactions(period_start, period_end);

-- Table: spending_transactions
CREATE TABLE IF NOT EXISTS spending_transactions (
    id SERIAL PRIMARY KEY,
    spending_id INTEGER NOT NULL REFERENCES additional_spendings(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    transaction_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_spending_transactions_spending_id ON spending_transactions(spending_id);
CREATE INDEX IF NOT EXISTS idx_spending_transactions_status ON spending_transactions(status);

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts for the application';
COMMENT ON TABLE companies IS 'Company information linked to users';
COMMENT ON TABLE departments IS 'Departments within companies';
COMMENT ON TABLE workers IS 'Workers/employees assigned to departments';
COMMENT ON TABLE additional_spendings IS 'Additional spending records';
COMMENT ON TABLE revenues IS 'Revenue records by month and year';
COMMENT ON TABLE payroll_transactions IS 'Payroll payment transactions';
COMMENT ON TABLE spending_transactions IS 'Spending payment transactions';

