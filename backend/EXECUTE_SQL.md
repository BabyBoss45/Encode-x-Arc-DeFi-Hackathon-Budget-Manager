# Как выполнить SQL скрипт

## Вариант 1: В SQL редакторе (DBeaver, pgAdmin, DataGrip и т.д.)

1. **Откройте файл** `backend/postgresql_schema.sql` в текстовом редакторе
2. **Скопируйте ВСЁ содержимое** файла (Ctrl+A, Ctrl+C)
3. **Вставьте в SQL редактор** вашего инструмента (вкладка Query)
4. **Убедитесь, что подключены к базе данных** `bossboard`
5. **Выполните запрос** (кнопка Execute или F5)

## Вариант 2: Через командную строку (psql)

Откройте **PowerShell** или **Command Prompt** (НЕ SQL редактор!) и выполните:

```powershell
# Перейдите в папку проекта
cd D:\Encode-x-Arc-DeFi-Hackathon-Budget-Manager

# Выполните SQL скрипт
psql -U postgres -d bossboard -f backend/postgresql_schema.sql
```

Если потребуется пароль, введите пароль пользователя postgres.

## Вариант 3: Через pgAdmin

1. Откройте pgAdmin
2. Подключитесь к серверу PostgreSQL
3. Правой кнопкой на базе данных `bossboard` → **Query Tool**
4. Нажмите **Open File** (иконка папки)
5. Выберите файл `backend/postgresql_schema.sql`
6. Нажмите **Execute** (F5)

## Проверка результата

После выполнения вы должны увидеть сообщения:
- `CREATE TABLE`
- `CREATE INDEX`

Проверьте, что таблицы созданы:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

Должно быть 8 таблиц:
- users
- companies
- departments
- workers
- additional_spendings
- revenues
- payroll_transactions
- spending_transactions

