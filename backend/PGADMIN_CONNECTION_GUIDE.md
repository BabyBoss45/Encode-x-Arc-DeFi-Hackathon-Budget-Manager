# Как подключиться к базе данных через pgAdmin

## Проблема
Приложение использует ngrok для подключения, но в pgAdmin вы подключаетесь к localhost напрямую.

## Решение

### Вариант 1: Подключение через ngrok (рекомендуется)

В pgAdmin при создании сервера используйте:

**Host name/address:**
```
5.tcp.eu.ngrok.io
```

**Port:**
```
14257
```

**Maintenance database:**
```
bossboard
```

**Username:**
```
postgres
```

**Password:**
```
admin
```

⚠️ **Важно:** Адрес ngrok (`5.tcp.eu.ngrok.io:14257`) меняется при каждом перезапуске ngrok. После перезапуска обновите настройки подключения в pgAdmin.

---

### Вариант 2: Подключение к localhost (если ngrok не нужен)

Если вы хотите подключаться напрямую к локальной базе данных:

**Host name/address:**
```
localhost
```

**Port:**
```
5432
```

**Maintenance database:**
```
bossboard
```

**Username:**
```
postgres
```

**Password:**
```
admin
```

---

## Проверка подключения

После подключения выполните этот SQL запрос:

```sql
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
```

Должно показать:
- users: 2
- companies: 2
- departments: 4
- workers: 5
- additional_spendings: 3
- revenues: 3

---

## Если данные не видны

1. **Проверьте имя базы данных:**
   ```sql
   SELECT current_database();
   ```
   Должно быть: `bossboard`

2. **Проверьте схему:**
   ```sql
   SELECT current_schema();
   ```
   Должно быть: `public`

3. **Проверьте таблицы:**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

4. **Проверьте данные:**
   ```sql
   SELECT * FROM users;
   ```

---

## Текущие настройки приложения

Ваше приложение использует:
- **Host:** `5.tcp.eu.ngrok.io`
- **Port:** `14257`
- **Database:** `bossboard`
- **User:** `postgres`
- **Password:** `admin`

Используйте те же настройки в pgAdmin!

