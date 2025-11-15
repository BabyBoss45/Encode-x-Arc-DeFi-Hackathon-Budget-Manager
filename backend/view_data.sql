-- Скрипт для просмотра всех данных в базе данных

-- 1. Просмотр всех пользователей
SELECT id, email, company_name, created_at 
FROM users 
ORDER BY created_at DESC;

-- 2. Просмотр компаний
SELECT c.id, c.user_id, u.email, u.company_name, c.master_wallet_address, c.payroll_date, c.payroll_time
FROM companies c
JOIN users u ON c.user_id = u.id
ORDER BY c.created_at DESC;

-- 3. Просмотр всех департаментов
SELECT d.id, d.company_id, u.company_name, d.name, d.created_at
FROM departments d
JOIN companies c ON d.company_id = c.id
JOIN users u ON c.user_id = u.id
ORDER BY d.created_at DESC;

-- 4. Просмотр всех работников
SELECT w.id, w.department_id, d.name as department_name, 
       w.name, w.surname, w.salary, w.wallet_address, w.is_active, w.created_at
FROM workers w
JOIN departments d ON w.department_id = d.id
ORDER BY w.created_at DESC;

-- 5. Просмотр всех расходов (spendings)
SELECT s.id, s.company_id, u.company_name, 
       d.name as department_name, s.name, s.amount, s.wallet_address, s.created_at
FROM additional_spendings s
JOIN companies c ON s.company_id = c.id
JOIN users u ON c.user_id = u.id
LEFT JOIN departments d ON s.department_id = d.id
ORDER BY s.created_at DESC;

-- 6. Просмотр всех доходов (revenues)
SELECT r.id, r.company_id, u.company_name, r.amount, r.month, r.year, r.created_at
FROM revenues r
JOIN companies c ON r.company_id = c.id
JOIN users u ON c.user_id = u.id
ORDER BY r.year DESC, r.month DESC;

-- 7. Просмотр транзакций зарплат
SELECT pt.id, pt.company_id, u.company_name, 
       w.name || ' ' || w.surname as worker_name,
       pt.amount, pt.period_start, pt.period_end, pt.status, pt.transaction_hash, pt.created_at
FROM payroll_transactions pt
JOIN companies c ON pt.company_id = c.id
JOIN users u ON c.user_id = u.id
JOIN workers w ON pt.worker_id = w.id
ORDER BY pt.created_at DESC;

-- 8. Просмотр транзакций расходов
SELECT st.id, st.spending_id, s.name as spending_name, 
       st.amount, st.status, st.transaction_hash, st.created_at
FROM spending_transactions st
JOIN additional_spendings s ON st.spending_id = s.id
ORDER BY st.created_at DESC;

-- 9. Статистика по компании (для конкретного пользователя - замените USER_ID)
-- SELECT 
--     u.company_name,
--     COUNT(DISTINCT d.id) as total_departments,
--     COUNT(DISTINCT w.id) as total_workers,
--     COUNT(DISTINCT CASE WHEN w.is_active THEN w.id END) as active_workers,
--     SUM(w.salary) as total_payroll,
--     SUM(s.amount) as total_spendings,
--     SUM(r.amount) as total_revenue
-- FROM users u
-- LEFT JOIN companies c ON u.id = c.user_id
-- LEFT JOIN departments d ON c.id = d.company_id
-- LEFT JOIN workers w ON d.id = w.department_id
-- LEFT JOIN additional_spendings s ON c.id = s.company_id
-- LEFT JOIN revenues r ON c.id = r.company_id
-- WHERE u.id = 1  -- Замените на ваш user_id
-- GROUP BY u.id, u.company_name;

-- 10. Просмотр всех таблиц и количества записей
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

