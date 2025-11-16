# Как перезапустить Backend и Frontend

## Быстрый способ (используя скрипты):

### 1. Остановить текущие процессы (если запущены):
```bash
# Остановить backend (порт 8000)
lsof -ti:8000 | xargs kill -9

# Остановить frontend (порт 8001)
lsof -ti:8001 | xargs kill -9
```

### 2. Запустить Backend:
```bash
cd backend
python3 main.py
```
Или используйте скрипт:
```bash
./start_backend.sh
```

Backend будет доступен на: `http://localhost:8000`

### 3. Запустить Frontend (в новом терминале):
```bash
cd src
python3 frontend.py
```
Или используйте скрипт:
```bash
./start_frontend.sh
```

Frontend будет доступен на: `http://localhost:8001`

---

## Альтернативный способ (через uvicorn напрямую):

### Backend:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend:
```bash
cd src
uvicorn frontend:app --reload --host 0.0.0.0 --port 8001
```

---

## Проверка, что все работает:

1. Откройте браузер и перейдите на `http://localhost:8001`
2. Войдите в систему
3. Откройте Dashboard
4. Проверьте раздел "Transaction history" - должны отображаться:
   - **Тип транзакции**: Deposit, Withdrawal, Transfer
   - **Статус транзакции**: Complete (зеленый), Pending (оранжевый), Failed (красный)

---

## Если что-то не работает:

1. Проверьте логи в консоли backend - там должны быть сообщения `[DEBUG]`
2. Убедитесь, что в базе данных есть `circle_wallet_id` для вашей компании
3. Проверьте, что Circle API ключ настроен в `.env` файле

