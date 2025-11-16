-- Простой SQL скрипт для очистки базы данных
-- Использует TRUNCATE для быстрой очистки (PostgreSQL)

-- Отключаем проверку внешних ключей
SET session_replication_role = 'replica';

-- Очищаем все таблицы
TRUNCATE TABLE payroll_transactions CASCADE;
TRUNCATE TABLE spending_transactions CASCADE;
TRUNCATE TABLE additional_spendings CASCADE;
TRUNCATE TABLE revenues CASCADE;
TRUNCATE TABLE workers CASCADE;
TRUNCATE TABLE departments CASCADE;
TRUNCATE TABLE companies CASCADE;
TRUNCATE TABLE users CASCADE;

-- Включаем проверку внешних ключей обратно
SET session_replication_role = 'origin';

-- Сброс последовательностей (auto-increment счетчиков)
ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS companies_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS departments_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS workers_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS additional_spendings_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS revenues_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS payroll_transactions_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS spending_transactions_id_seq RESTART WITH 1;

