-- Запросы для просмотра всех данных в pgAdmin
-- Выполняйте по одному запросу или все сразу

-- 1. Просмотр всех пользователей
SELECT id, email, company_name, created_at 
FROM users 
ORDER BY id;

-- 2. Просмотр всех компаний
SELECT c.id, u.email, u.company_name, c.master_wallet_address, c.payroll_date
FROM companies c
JOIN users u ON c.user_id = u.id
ORDER BY c.id;

-- 3. Просмотр всех департаментов
SELECT d.id, u.company_name, d.name, d.created_at
FROM departments d
JOIN companies c ON d.company_id = c.id
JOIN users u ON c.user_id = u.id
ORDER BY d.id;

-- 4. Просмотр всех работников
SELECT w.id, d.name as department, w.name, w.surname, w.salary, w.wallet_address, w.is_active
FROM workers w
JOIN departments d ON w.department_id = d.id
ORDER BY w.id;

-- 5. Просмотр всех расходов
SELECT s.id, u.company_name, COALESCE(d.name, 'CEO') as department, s.name, s.amount, s.wallet_address
FROM additional_spendings s
JOIN companies c ON s.company_id = c.id
JOIN users u ON c.user_id = u.id
LEFT JOIN departments d ON s.department_id = d.id
ORDER BY s.id;

-- 6. Просмотр всех доходов
SELECT r.id, u.company_name, r.amount, r.month, r.year, r.created_at
FROM revenues r
JOIN companies c ON r.company_id = c.id
JOIN users u ON c.user_id = u.id
ORDER BY r.year DESC, r.month DESC;

-- 7. Статистика (количество записей)
SELECT 
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'companies', COUNT(*) FROM companies
UNION ALL
SELECT 'departments', COUNT(*) FROM departments
UNION ALL
SELECT 'workers', COUNT(*) FROM workers
UNION ALL
SELECT 'additional_spendings', COUNT(*) FROM additional_spendings
UNION ALL
SELECT 'revenues', COUNT(*) FROM revenues;

