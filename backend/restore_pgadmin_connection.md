# Восстановление соединения с pgAdmin

## Проблема
Соединение с pgAdmin сервером потеряно. Это обычно происходит, когда:
1. ngrok туннель был закрыт или перезапущен (адрес изменился)
2. PostgreSQL сервер был перезапущен
3. Изменились настройки сети

## Решение

### Шаг 1: Проверить статус PostgreSQL
PostgreSQL должен работать на порту 5432. Проверьте:
```powershell
netstat -ano | findstr :5432
```

### Шаг 2: Запустить ngrok туннель

Если используете ngrok для доступа из интернета:

1. Откройте новый терминал
2. Запустите ngrok:
```bash
ngrok tcp 5432
```

3. Скопируйте новый адрес (например: `tcp://5.tcp.eu.ngrok.io:14257`)

### Шаг 3: Обновить настройки подключения в pgAdmin

1. Откройте pgAdmin
2. Правой кнопкой на сервере → Properties
3. Перейдите на вкладку "Connection"
4. Обновите:
   - **Host**: адрес из ngrok (например: `5.tcp.eu.ngrok.io`)
   - **Port**: порт из ngrok (например: `14257`)
   - **Username**: `postgres`
   - **Password**: `admin` (или ваш пароль)

### Шаг 4: Обновить .env файл

Если адрес ngrok изменился, обновите `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:admin@НОВЫЙ_АДРЕС_ngrok:НОВЫЙ_ПОРТ/bossboard
```

### Альтернатива: Использовать localhost

Если pgAdmin запущен на том же компьютере, где PostgreSQL:
- **Host**: `localhost` или `127.0.0.1`
- **Port**: `5432`
- **Username**: `postgres`
- **Password**: `admin`

## Быстрая проверка соединения

Проверьте соединение через Python:
```bash
cd backend
python -c "from src.database import SessionLocal; db = SessionLocal(); print('Connection OK!'); db.close()"
```

