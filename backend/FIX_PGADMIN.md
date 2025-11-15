# Как увидеть данные в pgAdmin

## Проблема
Вы подключены к базе данных `bossboard`, но не видите данные.

## Решение

### Шаг 1: Проверьте подключение

В pgAdmin выполните этот SQL запрос (Query Tool → вставьте запрос → Execute):

```sql
SELECT 
    current_database() as database_name,
    current_user as user_name,
    inet_server_addr() as server_address,
    inet_server_port() as server_port;
```

**Ожидаемый результат:**
- `database_name` = `bossboard`
- `user_name` = `postgres`
- `server_address` = адрес ngrok (или `::1` для localhost)
- `server_port` = `14257` (если через ngrok) или `5432` (если localhost)

---

### Шаг 2: Проверьте данные

Выполните этот запрос:

```sql
SELECT COUNT(*) FROM users;
```

**Должно показать:** `2`

Если показывает `0` или ошибку → вы подключены к другой базе данных или серверу.

---

### Шаг 3: Просмотр всех данных

Выполните запросы из файла `backend/check_data_in_pgadmin.sql`:

1. Откройте Query Tool в pgAdmin (правой кнопкой на базе `bossboard` → Query Tool)
2. Скопируйте запросы из `backend/check_data_in_pgadmin.sql`
3. Выполните их (F5 или кнопка Execute)

---

## Если данные не видны

### Вариант 1: Неправильное подключение к серверу

Проверьте настройки сервера `BudgetDB` в pgAdmin:

1. Правой кнопкой на `BudgetDB` → Properties
2. Вкладка **Connection**
3. Проверьте:
   - **Host:** должно быть `5.tcp.eu.ngrok.io` (для ngrok) или `localhost` (для прямого подключения)
   - **Port:** должно быть `14257` (для ngrok) или `5432` (для localhost)
   - **Database:** `bossboard`
   - **Username:** `postgres`
   - **Password:** `admin`

### Вариант 2: Подключение к другой базе данных

Убедитесь, что вы выбрали правильную базу данных:
- В дереве слева выберите: **Servers → BudgetDB → Databases → bossboard**
- База `bossboard` должна быть выделена синим

### Вариант 3: Данные в другой схеме

Проверьте схему:

```sql
SELECT current_schema();
```

Должно быть: `public`

Если нет, переключитесь:

```sql
SET search_path TO public;
```

---

## Быстрая проверка всех таблиц

```sql
SELECT 
    schemaname,
    tablename,
    (SELECT COUNT(*) FROM information_schema.tables t2 
     WHERE t2.table_schema = t1.schemaname 
     AND t2.table_name = t1.tablename) as exists
FROM pg_tables t1
WHERE schemaname = 'public'
ORDER BY tablename;
```

---

## Просмотр данных по таблицам

### Пользователи:
```sql
SELECT * FROM users;
```

### Компании:
```sql
SELECT * FROM companies;
```

### Департаменты:
```sql
SELECT * FROM departments;
```

### Работники:
```sql
SELECT * FROM workers;
```

### Расходы:
```sql
SELECT * FROM additional_spendings;
```

### Доходы:
```sql
SELECT * FROM revenues;
```

---

## Если ничего не помогает

1. **Переподключитесь к серверу:**
   - Правой кнопкой на `BudgetDB` → Disconnect Server
   - Затем Connect Server

2. **Создайте новое подключение:**
   - Правой кнопкой на "Servers" → Register → Server
   - Используйте настройки из `.env` файла

3. **Проверьте через Python:**
   ```powershell
   cd backend
   py check_connection.py
   ```

