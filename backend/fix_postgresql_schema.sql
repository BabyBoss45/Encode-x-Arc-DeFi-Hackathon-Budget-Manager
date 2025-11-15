-- Скрипт для исправления структуры существующих таблиц PostgreSQL
-- Выполните этот скрипт если получили ошибки о недостающих колонках

-- Сначала проверим и удалим существующие таблицы (если нужно пересоздать)
-- ВНИМАНИЕ: Это удалит все данные! Используйте только если база пустая или данные не важны

-- Удаление таблиц в правильном порядке (с учетом внешних ключей)
DROP TABLE IF EXISTS spending_transactions CASCADE;
DROP TABLE IF EXISTS payroll_transactions CASCADE;
DROP TABLE IF EXISTS revenues CASCADE;
DROP TABLE IF EXISTS additional_spendings CASCADE;
DROP TABLE IF EXISTS workers CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Теперь создаем таблицы заново с правильной структурой

-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Table: companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    master_wallet_address VARCHAR(255),
    payroll_date DATE,
    payroll_time VARCHAR(5),  -- Format: HH:MM (24-hour)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_companies_user_id ON companies(user_id);

-- Table: departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_company_id ON departments(company_id);

-- Table: workers
CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    salary DOUBLE PRECISION NOT NULL,
    wallet_address VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workers_department_id ON workers(department_id);
CREATE INDEX idx_workers_is_active ON workers(is_active);

-- Table: additional_spendings
CREATE TABLE additional_spendings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    wallet_address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_spendings_company_id ON additional_spendings(company_id);
CREATE INDEX idx_spendings_department_id ON additional_spendings(department_id);

-- Table: revenues
CREATE TABLE revenues (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    year INTEGER NOT NULL CHECK (year >= 2000 AND year <= 2100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_revenues_company_id ON revenues(company_id);
CREATE INDEX idx_revenues_year_month ON revenues(year DESC, month DESC);

-- Table: payroll_transactions
CREATE TABLE payroll_transactions (
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

CREATE INDEX idx_payroll_company_id ON payroll_transactions(company_id);
CREATE INDEX idx_payroll_worker_id ON payroll_transactions(worker_id);
CREATE INDEX idx_payroll_status ON payroll_transactions(status);
CREATE INDEX idx_payroll_period ON payroll_transactions(period_start, period_end);

-- Table: spending_transactions
CREATE TABLE spending_transactions (
    id SERIAL PRIMARY KEY,
    spending_id INTEGER NOT NULL REFERENCES additional_spendings(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    transaction_hash VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_spending_transactions_spending_id ON spending_transactions(spending_id);
CREATE INDEX idx_spending_transactions_status ON spending_transactions(status);

-- Проверка структуры
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;

