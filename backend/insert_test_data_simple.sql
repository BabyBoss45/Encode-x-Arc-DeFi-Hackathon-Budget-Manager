-- Простой скрипт для добавления тестовых данных
-- Используйте этот скрипт, если предыдущий не работает

-- 1. Пользователь (пароль: test123)
INSERT INTO users (email, password_hash, company_name, created_at)
VALUES ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJqZ5Z5Z5', 'Test Company', NOW())
ON CONFLICT (email) DO NOTHING;

-- 2. Компания
INSERT INTO companies (user_id, master_wallet_address, payroll_date, payroll_time, created_at)
VALUES (
    (SELECT id FROM users WHERE email = 'test@example.com'),
    '0x1234567890123456789012345678901234567890',
    CURRENT_DATE + INTERVAL '1 day',
    '09:00',
    NOW()
)
ON CONFLICT (user_id) DO NOTHING;

-- 3. Департаменты
INSERT INTO departments (company_id, name, created_at)
VALUES 
    ((SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com')), 'Engineering', NOW()),
    ((SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com')), 'Marketing', NOW()),
    ((SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com')), 'Sales', NOW()),
    ((SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com')), 'HR', NOW())
ON CONFLICT DO NOTHING;

-- 4. Работники
INSERT INTO workers (department_id, name, surname, salary, wallet_address, is_active, created_at)
SELECT 
    d.id,
    name,
    surname,
    salary,
    wallet_address,
    TRUE,
    NOW()
FROM departments d
CROSS JOIN (VALUES 
    ('John', 'Doe', 5000.0, '0x1111111111111111111111111111111111111111'),
    ('Jane', 'Smith', 6000.0, '0x2222222222222222222222222222222222222222'),
    ('Bob', 'Johnson', 5500.0, '0x3333333333333333333333333333333333333333')
) AS t(name, surname, salary, wallet_address)
WHERE d.company_id = (SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com'))
LIMIT 3;

-- 5. Расходы
INSERT INTO additional_spendings (company_id, department_id, name, amount, wallet_address, created_at)
SELECT 
    c.id,
    d.id,
    'Office Supplies',
    500.0,
    '0x7777777777777777777777777777777777777777',
    NOW()
FROM companies c
JOIN departments d ON c.id = d.company_id
WHERE c.user_id = (SELECT id FROM users WHERE email = 'test@example.com')
AND d.name = 'Marketing'
LIMIT 1;

-- 6. Доходы
INSERT INTO revenues (company_id, amount, month, year, created_at)
VALUES 
    ((SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com')), 50000.0, EXTRACT(MONTH FROM CURRENT_DATE)::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER, NOW()),
    ((SELECT id FROM companies WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com')), 55000.0, EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')::INTEGER, NOW())
ON CONFLICT DO NOTHING;

