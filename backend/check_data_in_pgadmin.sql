-- Скрипт для проверки данных в pgAdmin
-- Выполните эти запросы в Query Tool в pgAdmin

-- 1. Проверка подключения и сервера
SELECT 
    current_database() as database_name,
    current_user as user_name,
    inet_server_addr() as server_address,
    inet_server_port() as server_port;

-- 2. Проверка количества записей в таблицах
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
SELECT 'revenues', COUNT(*) FROM revenues
UNION ALL
SELECT 'payroll_transactions', COUNT(*) FROM payroll_transactions
UNION ALL
SELECT 'spending_transactions', COUNT(*) FROM spending_transactions;

-- 3. Просмотр пользователей
SELECT id, email, company_name, created_at 
FROM users 
ORDER BY id;

-- 4. Просмотр компаний
SELECT c.id, u.email, u.company_name, c.master_wallet_address
FROM companies c
JOIN users u ON c.user_id = u.id;

-- 5. Просмотр департаментов
SELECT d.id, u.company_name, d.name
FROM departments d
JOIN companies c ON d.company_id = c.id
JOIN users u ON c.user_id = u.id;

-- 6. Просмотр работников
SELECT w.id, d.name as department, w.name, w.surname, w.salary, w.is_active
FROM workers w
JOIN departments d ON w.department_id = d.id
ORDER BY w.id;

