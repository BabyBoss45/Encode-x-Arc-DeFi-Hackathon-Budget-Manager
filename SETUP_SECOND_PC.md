# Настройка на втором ПК - Пошаговая инструкция

## Что нужно на втором ПК

1. ✅ Python 3.8+ установлен
2. ✅ Код проекта скопирован
3. ✅ Зависимости установлены
4. ✅ Файл `.env` настроен правильно
5. ✅ Ngrok запущен на первом ПК

---

## Шаг 1: Установка Python

Если Python не установлен:
1. Скачайте с https://www.python.org/downloads/
2. При установке отметьте **"Add Python to PATH"**
3. Проверьте: `python --version` или `py --version`

---

## Шаг 2: Копирование проекта

Скопируйте всю папку проекта на второй ПК:
- Через USB
- Через сеть
- Через Git (если проект в репозитории)

---

## Шаг 3: Установка зависимостей

Откройте терминал в папке проекта:

```powershell
# Перейдите в папку проекта
cd D:\Encode-x-Arc-DeFi-Hackathon-Budget-Manager

# Установите зависимости backend
cd backend
pip install -r requirements.txt

# Вернитесь в корень
cd ..

# Установите зависимости frontend (если используете Python frontend)
pip install fastapi uvicorn jinja2 python-multipart requests
```

---

## Шаг 4: Настройка .env файла

**ВАЖНО:** Убедитесь, что ngrok запущен на первом ПК!

1. Откройте файл `backend/.env`
2. Убедитесь, что там правильный ngrok адрес:

```env
DATABASE_URL=postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard
JWT_SECRET_KEY=my-secret-key-change-in-production-12345
CIRCLE_API_KEY=test-key
CIRCLE_BASE_URL=https://api.circle.com/v1
```

⚠️ **Важно:** 
- Замените `5.tcp.eu.ngrok.io:14257` на актуальный ngrok адрес с первого ПК
- Ngrok адрес меняется при каждом перезапуске ngrok!

---

## Шаг 5: Проверка подключения к базе данных

```powershell
cd backend
python -c "import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); print('SUCCESS: Connected!'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(f'Users in DB: {cursor.fetchone()[0]}'); conn.close()"
```

**Ожидаемый результат:**
```
SUCCESS: Connected!
Users in DB: 2
```

Если ошибка → проверьте:
- Ngrok запущен на первом ПК?
- Правильный адрес в `.env`?
- Интернет работает?

---

## Шаг 6: Запуск backend

```powershell
cd backend
python main.py
```

**Ожидаемый результат:**
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Если ошибка → проверьте:
- Все зависимости установлены?
- Порт 8000 свободен?

---

## Шаг 7: Запуск frontend

Откройте **новый терминал**:

```powershell
# Из корневой папки проекта
python run_frontend.py

# ИЛИ
cd src
python frontend.py
```

**Ожидаемый результат:**
```
INFO:     Started server process [XXXXX]
INFO:     Uvicorn running on http://127.0.0.1:8001
```

---

## Шаг 8: Открытие в браузере

Откройте браузер и перейдите:
- Frontend: http://localhost:8001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Частые проблемы и решения

### Проблема 1: "ModuleNotFoundError"

**Решение:**
```powershell
pip install -r backend/requirements.txt
pip install fastapi uvicorn jinja2 python-multipart requests
```

---

### Проблема 2: "Connection refused" или "Connection timeout"

**Причины:**
- Ngrok не запущен на первом ПК
- Неправильный адрес в `.env`
- Интернет не работает

**Решение:**
1. Проверьте, что ngrok запущен на первом ПК: `ngrok tcp 5432`
2. Проверьте адрес в `.env` - должен совпадать с ngrok адресом
3. Проверьте интернет соединение

---

### Проблема 3: "Port 8000 already in use"

**Решение:**
```powershell
# Windows: найти процесс на порту 8000
netstat -ano | findstr :8000

# Остановить процесс (замените PID на реальный)
taskkill /PID <PID> /F
```

Или измените порт в `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Измените порт
```

---

### Проблема 4: "password authentication failed"

**Решение:**
Проверьте пароль в `.env`:
```env
DATABASE_URL=postgresql://postgres:admin@5.tcp.eu.ngrok.io:14257/bossboard
```
Пароль должен быть `admin` (или тот, который вы установили)

---

### Проблема 5: "No module named 'dotenv'"

**Решение:**
```powershell
pip install python-dotenv
```

---

## Проверочный чеклист

Перед запуском убедитесь:

- [ ] Python установлен (`python --version`)
- [ ] Проект скопирован на второй ПК
- [ ] Зависимости установлены (`pip install -r backend/requirements.txt`)
- [ ] Файл `backend/.env` создан и настроен
- [ ] Ngrok запущен на первом ПК (`ngrok tcp 5432`)
- [ ] Адрес в `.env` совпадает с ngrok адресом
- [ ] Подключение к базе работает (проверка через Python)
- [ ] Порты 8000 и 8001 свободны

---

## Быстрая команда для проверки всего

```powershell
# Проверка Python
python --version

# Проверка зависимостей
pip list | findstr "fastapi psycopg2"

# Проверка подключения
cd backend
python -c "import psycopg2; import os; from dotenv import load_dotenv; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); print('OK'); conn.close()"
```

---

## Если ничего не помогает

1. **Проверьте логи:**
   - Backend: смотрите вывод в терминале
   - Frontend: смотрите вывод в терминале

2. **Проверьте файлы:**
   - Существует ли `backend/.env`?
   - Правильный ли формат `DATABASE_URL`?

3. **Проверьте сеть:**
   - Работает ли интернет на втором ПК?
   - Может быть блокирует firewall?

4. **Попробуйте другой способ:**
   - Используйте облачную базу данных (Supabase/Railway) вместо ngrok

---

## Альтернатива: Использование облачной базы данных

Если ngrok не работает, используйте облачную базу:

1. Создайте базу на **Supabase** (бесплатно): https://supabase.com
2. Получите Connection String
3. Используйте его в `.env` на обоих ПК

Это проще и надежнее, чем ngrok!

