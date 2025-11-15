# SQL Запросы для PostgreSQL

Этот документ содержит все SQL запросы, которые используются в приложении BossBoard.

## Структура базы данных

### Таблицы

1. **users** - Пользователи системы
2. **companies** - Компании (связаны с пользователями)
3. **departments** - Департаменты (принадлежат компаниям)
4. **workers** - Работники (принадлежат департаментам)
5. **additional_spendings** - Дополнительные расходы
6. **revenues** - Доходы по месяцам
7. **payroll_transactions** - Транзакции выплаты зарплат
8. **spending_transactions** - Транзакции расходов

## Основные SQL запросы

### Аутентификация

#### Регистрация пользователя
```sql
INSERT INTO users (email, password_hash, company_name)
VALUES ('user@example.com', 'hashed_password', 'Company Name')
RETURNING id, created_at;
```

#### Создание компании для пользователя
```sql
INSERT INTO companies (user_id, master_wallet_address, payroll_date, payroll_time)
VALUES (1, NULL, NULL, NULL)
RETURNING id, created_at;
```

#### Поиск пользователя по email
```sql
SELECT id, email, password_hash, company_name, created_at
FROM users
WHERE email = 'user@example.com'
LIMIT 1;
```

### Департаменты

#### Получить все департаменты компании
```sql
SELECT id, company_id, name, created_at
FROM departments
WHERE company_id = 1
ORDER BY created_at DESC;
```

#### Создать департамент
```sql
INSERT INTO departments (company_id, name)
VALUES (1, 'Engineering')
RETURNING id, created_at;
```

#### Удалить департамент
```sql
DELETE FROM departments
WHERE id = 1 AND company_id = 1;
```

### Работники

#### Получить всех работников компании
```sql
SELECT w.id, w.department_id, w.name, w.surname, w.salary, 
       w.wallet_address, w.is_active, w.created_at
FROM workers w
JOIN departments d ON w.department_id = d.id
WHERE d.company_id = 1;
```

#### Получить работников департамента
```sql
SELECT id, department_id, name, surname, salary, 
       wallet_address, is_active, created_at
FROM workers
WHERE department_id = 1 AND is_active = TRUE;
```

#### Создать работника
```sql
INSERT INTO workers (department_id, name, surname, salary, wallet_address, is_active)
VALUES (1, 'John', 'Doe', 5000.00, '0x1234...', TRUE)
RETURNING id, created_at;
```

#### Обновить статус работника
```sql
UPDATE workers
SET is_active = FALSE
WHERE id = 1;
```

#### Подсчет общей зарплаты активных работников
```sql
SELECT COALESCE(SUM(w.salary), 0) as total_payroll
FROM workers w
JOIN departments d ON w.department_id = d.id
WHERE d.company_id = 1 AND w.is_active = TRUE;
```

### Расходы (Spendings)

#### Получить все расходы компании
```sql
SELECT id, company_id, department_id, name, amount, 
       wallet_address, created_at
FROM additional_spendings
WHERE company_id = 1
ORDER BY created_at DESC;
```

#### Получить расходы департамента
```sql
SELECT id, company_id, department_id, name, amount, 
       wallet_address, created_at
FROM additional_spendings
WHERE department_id = 1;
```

#### Получить расходы CEO (без департамента)
```sql
SELECT id, company_id, department_id, name, amount, 
       wallet_address, created_at
FROM additional_spendings
WHERE company_id = 1 AND department_id IS NULL;
```

#### Создать расход
```sql
INSERT INTO additional_spendings (company_id, department_id, name, amount, wallet_address)
VALUES (1, 1, 'Office Supplies', 500.00, '0x5678...')
RETURNING id, created_at;
```

#### Подсчет общей суммы расходов
```sql
SELECT COALESCE(SUM(amount), 0) as total_spendings
FROM additional_spendings
WHERE company_id = 1;
```

### Доходы (Revenues)

#### Получить все доходы компании
```sql
SELECT id, company_id, amount, month, year, created_at
FROM revenues
WHERE company_id = 1
ORDER BY year DESC, month DESC;
```

#### Создать доход
```sql
INSERT INTO revenues (company_id, amount, month, year)
VALUES (1, 10000.00, 11, 2024)
RETURNING id, created_at;
```

#### Подсчет общей суммы доходов
```sql
SELECT COALESCE(SUM(amount), 0) as total_revenue
FROM revenues
WHERE company_id = 1;
```

### Транзакции зарплат (Payroll Transactions)

#### Получить все транзакции компании
```sql
SELECT id, company_id, worker_id, amount, period_start, 
       period_end, status, transaction_hash, created_at
FROM payroll_transactions
WHERE company_id = 1
ORDER BY created_at DESC;
```

#### Получить транзакции работника
```sql
SELECT id, company_id, worker_id, amount, period_start, 
       period_end, status, transaction_hash, created_at
FROM payroll_transactions
WHERE worker_id = 1
ORDER BY created_at DESC;
```

#### Создать транзакцию зарплаты
```sql
INSERT INTO payroll_transactions 
    (company_id, worker_id, amount, period_start, period_end, status)
VALUES (1, 1, 5000.00, '2024-11-01', '2024-11-30', 'pending')
RETURNING id, created_at;
```

#### Обновить статус транзакции
```sql
UPDATE payroll_transactions
SET status = 'completed', transaction_hash = '0xabc123...'
WHERE id = 1;
```

### Транзакции расходов (Spending Transactions)

#### Получить транзакции расхода
```sql
SELECT id, spending_id, amount, transaction_hash, status, created_at
FROM spending_transactions
WHERE spending_id = 1
ORDER BY created_at DESC;
```

#### Создать транзакцию расхода
```sql
INSERT INTO spending_transactions (spending_id, amount, status)
VALUES (1, 500.00, 'pending')
RETURNING id, created_at;
```

## Статистика Dashboard

### Общая статистика компании
```sql
-- Количество работников
SELECT COUNT(*) as total_workers
FROM workers w
JOIN departments d ON w.department_id = d.id
WHERE d.company_id = 1 AND w.is_active = TRUE;

-- Количество департаментов
SELECT COUNT(*) as total_departments
FROM departments
WHERE company_id = 1;

-- Общая зарплата
SELECT COALESCE(SUM(w.salary), 0) as total_payroll
FROM workers w
JOIN departments d ON w.department_id = d.id
WHERE d.company_id = 1 AND w.is_active = TRUE;

-- Общие расходы
SELECT COALESCE(SUM(amount), 0) as total_spendings
FROM additional_spendings
WHERE company_id = 1;

-- Общие доходы
SELECT COALESCE(SUM(amount), 0) as total_revenue
FROM revenues
WHERE company_id = 1;
```

### Статистика по департаментам
```sql
SELECT 
    d.id,
    d.name,
    COUNT(w.id) as worker_count,
    COALESCE(SUM(w.salary), 0) as payroll,
    COALESCE(SUM(s.amount), 0) as spendings,
    COALESCE(SUM(w.salary), 0) + COALESCE(SUM(s.amount), 0) as total
FROM departments d
LEFT JOIN workers w ON w.department_id = d.id AND w.is_active = TRUE
LEFT JOIN additional_spendings s ON s.department_id = d.id
WHERE d.company_id = 1
GROUP BY d.id, d.name
ORDER BY total DESC;
```

## Индексы для оптимизации

Все индексы уже созданы в `postgresql_schema.sql`:

- `idx_users_email` - для быстрого поиска по email
- `idx_companies_user_id` - для связи user-company
- `idx_departments_company_id` - для фильтрации по компании
- `idx_workers_department_id` - для фильтрации работников
- `idx_workers_is_active` - для фильтрации активных работников
- `idx_spendings_company_id` - для фильтрации расходов
- `idx_spendings_department_id` - для фильтрации по департаменту
- `idx_revenues_company_id` - для фильтрации доходов
- `idx_revenues_year_month` - для сортировки по дате
- `idx_payroll_company_id`, `idx_payroll_worker_id` - для транзакций
- `idx_payroll_status` - для фильтрации по статусу

## Примеры сложных запросов

### Получить всех работников с информацией о департаменте
```sql
SELECT 
    w.id,
    w.name,
    w.surname,
    w.salary,
    w.wallet_address,
    w.is_active,
    d.name as department_name,
    c.company_name
FROM workers w
JOIN departments d ON w.department_id = d.id
JOIN companies c ON d.company_id = c.id
WHERE c.id = 1
ORDER BY d.name, w.surname;
```

### Получить последние транзакции зарплат с информацией о работниках
```sql
SELECT 
    pt.id,
    pt.amount,
    pt.period_start,
    pt.period_end,
    pt.status,
    pt.transaction_hash,
    w.name || ' ' || w.surname as worker_name,
    d.name as department_name
FROM payroll_transactions pt
JOIN workers w ON pt.worker_id = w.id
JOIN departments d ON w.department_id = d.id
WHERE pt.company_id = 1
ORDER BY pt.created_at DESC
LIMIT 10;
```

### Получить финансовую сводку по месяцам
```sql
SELECT 
    r.year,
    r.month,
    COALESCE(SUM(r.amount), 0) as revenue,
    COALESCE(SUM(pt.amount), 0) as payroll_expenses,
    COALESCE(SUM(s.amount), 0) as spending_expenses,
    COALESCE(SUM(r.amount), 0) - COALESCE(SUM(pt.amount), 0) - COALESCE(SUM(s.amount), 0) as profit
FROM revenues r
LEFT JOIN payroll_transactions pt ON 
    EXTRACT(YEAR FROM pt.period_start) = r.year AND
    EXTRACT(MONTH FROM pt.period_start) = r.month AND
    pt.company_id = r.company_id
LEFT JOIN additional_spendings s ON
    EXTRACT(YEAR FROM s.created_at) = r.year AND
    EXTRACT(MONTH FROM s.created_at) = r.month AND
    s.company_id = r.company_id
WHERE r.company_id = 1
GROUP BY r.year, r.month
ORDER BY r.year DESC, r.month DESC;
```

