-- SQL скрипт для очистки базы данных
-- Удаляет все данные из всех таблиц в правильном порядке (с учетом внешних ключей)

-- Отключаем проверку внешних ключей (для PostgreSQL)
SET session_replication_role = 'replica';

-- Удаляем данные из таблиц с зависимостями (сначала дочерние таблицы)
DELETE FROM payroll_transactions;
DELETE FROM spending_transactions;
DELETE FROM additional_spendings;
DELETE FROM revenues;
DELETE FROM workers;
DELETE FROM departments;
DELETE FROM companies;
DELETE FROM users;

-- Включаем проверку внешних ключей обратно
SET session_replication_role = 'origin';

-- Проверка: подсчет записей в каждой таблице (должно быть 0)
SELECT 
    'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 
    'companies', COUNT(*) FROM companies
UNION ALL
SELECT 
    'departments', COUNT(*) FROM departments
UNION ALL
SELECT 
    'workers', COUNT(*) FROM workers
UNION ALL
SELECT 
    'revenues', COUNT(*) FROM revenues
UNION ALL
SELECT 
    'additional_spendings', COUNT(*) FROM additional_spendings
UNION ALL
SELECT 
    'spending_transactions', COUNT(*) FROM spending_transactions
UNION ALL
SELECT 
    'payroll_transactions', COUNT(*) FROM payroll_transactions;

