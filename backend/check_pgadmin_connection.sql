-- Проверка подключения в pgAdmin
-- Выполните эти запросы, чтобы понять, к какой базе вы подключены

-- 1. Проверка текущей базы данных и сервера
SELECT 
    current_database() as "Database Name",
    current_user as "User",
    inet_server_addr() as "Server IP",
    inet_server_port() as "Server Port",
    version() as "PostgreSQL Version";

-- 2. Проверка всех баз данных на сервере
SELECT datname, datdba::regrole as owner, pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database
WHERE datistemplate = false
ORDER BY datname;

-- 3. Проверка схем в текущей базе
SELECT schema_name 
FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY schema_name;

-- 4. Проверка всех таблиц в схеме public
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns 
     WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;

