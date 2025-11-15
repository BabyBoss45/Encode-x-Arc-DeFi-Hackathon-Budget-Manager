-- Скрипт для добавления тестовых данных в базу данных

-- 1. Создание тестового пользователя
INSERT INTO users (email, password_hash, company_name, created_at)
VALUES ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJqZ5Z5Z5', 'Test Company', NOW())
ON CONFLICT (email) DO NOTHING
RETURNING id;

-- Получаем ID созданного пользователя (замените на реальный ID если нужно)
-- Обычно это будет 1, если база пустая

-- 2. Создание компании для пользователя
INSERT INTO companies (user_id, master_wallet_address, payroll_date, payroll_time, created_at)
SELECT 
    u.id,
    '0x1234567890123456789012345678901234567890',
    CURRENT_DATE + INTERVAL '1 day',
    '09:00',
    NOW()
FROM users u
WHERE u.email = 'test@example.com'
ON CONFLICT (user_id) DO NOTHING;

-- 3. Создание департаментов
INSERT INTO departments (company_id, name, created_at)
SELECT 
    c.id,
    dept_name,
    NOW()
FROM companies c
CROSS JOIN (VALUES 
    ('Engineering'),
    ('Marketing'),
    ('Sales'),
    ('HR')
) AS depts(dept_name)
WHERE c.user_id = (SELECT id FROM users WHERE email = 'test@example.com')
ON CONFLICT DO NOTHING;

-- 4. Создание работников
INSERT INTO workers (department_id, name, surname, salary, wallet_address, is_active, created_at)
SELECT 
    d.id,
    worker_data.name,
    worker_data.surname,
    worker_data.salary,
    worker_data.wallet_address,
    TRUE,
    NOW()
FROM departments d
CROSS JOIN (VALUES 
    ('John', 'Doe', 5000.0, '0x1111111111111111111111111111111111111111'),
    ('Jane', 'Smith', 6000.0, '0x2222222222222222222222222222222222222222'),
    ('Bob', 'Johnson', 5500.0, '0x3333333333333333333333333333333333333333'),
    ('Alice', 'Williams', 5200.0, '0x4444444444444444444444444444444444444444'),
    ('Charlie', 'Brown', 4800.0, '0x5555555555555555555555555555555555555555'),
    ('Diana', 'Davis', 5800.0, '0x6666666666666666666666666666666666666666')
) AS worker_data(name, surname, salary, wallet_address)
WHERE d.company_id = (SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com'))
LIMIT 6;

-- 5. Создание расходов
INSERT INTO additional_spendings (company_id, department_id, name, amount, wallet_address, created_at)
SELECT 
    c.id,
    d.id,
    spending_data.name,
    spending_data.amount,
    spending_data.wallet_address,
    NOW()
FROM companies c
CROSS JOIN departments d
CROSS JOIN (VALUES 
    ('Office Supplies', 500.0, '0x7777777777777777777777777777777777777777'),
    ('Software Licenses', 1200.0, '0x8888888888888888888888888888888888888888'),
    ('Marketing Campaign', 3000.0, '0x9999999999999999999999999999999999999999')
) AS spending_data(name, amount, wallet_address)
WHERE c.user_id = (SELECT id FROM users WHERE email = 'test@example.com')
AND d.name = 'Marketing'
LIMIT 3;

-- 6. Создание доходов (за последние 3 месяца)
INSERT INTO revenues (company_id, amount, month, year, created_at)
SELECT 
    c.id,
    revenue_data.amount,
    revenue_data.month,
    revenue_data.year,
    NOW()
FROM companies c
CROSS JOIN (VALUES 
    (50000.0, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '2 months')::INTEGER),
    (55000.0, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER),
    (60000.0, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER)
) AS revenue_data(amount, month, year)
WHERE c.user_id = (SELECT id FROM users WHERE email = 'test@example.com')
ON CONFLICT DO NOTHING;

-- Проверка созданных данных
SELECT 'Users:' as info, COUNT(*) as count FROM users
UNION ALL
SELECT 'Companies:', COUNT(*) FROM companies
UNION ALL
SELECT 'Departments:', COUNT(*) FROM departments
UNION ALL
SELECT 'Workers:', COUNT(*) FROM workers
UNION ALL
SELECT 'Spendings:', COUNT(*) FROM additional_spendings
UNION ALL
SELECT 'Revenues:', COUNT(*) FROM revenues;

