# Деплой Frontend на Railway (Backend на ngrok)

## Архитектура

- ✅ **Backend** - работает локально, доступен через ngrok
- ✅ **База данных** - PostgreSQL на ngrok (как настроено)
- ✅ **Frontend** - деплоится на Railway

---

## Шаг 1: Запуск Backend с ngrok

1. **Запустите backend локально:**
   ```powershell
   cd backend
   python main.py
   ```

2. **В другом терминале запустите ngrok для backend:**
   ```powershell
   .\start_ngrok_backend.ps1
   ```

3. **Скопируйте backend ngrok URL** (например: `https://abc123.ngrok.io`)

4. **Обновите `backend/.env`:**
   ```env
   DATABASE_URL=postgresql://postgres:admin@ваш-ngrok-хост:порт/bossboard
   FRONTEND_URL=https://your-frontend.railway.app
   ```
   ⚠️ Пока frontend URL еще неизвестен, добавьте его после деплоя frontend

---

## Шаг 2: Деплой Frontend на Railway

1. **Перейдите на https://railway.app**
2. **Войдите через GitHub**
3. **Создайте новый проект:**
   - Нажмите "Start a New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий

4. **Railway автоматически создаст сервис**

5. **Настройте Frontend сервис:**
   - В настройках сервиса (Settings → Deploy)
   - **Root Directory:** оставьте пустым (корень проекта `/`)
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements_frontend.txt`
   - **Start Command:** `cd src && python frontend.py`
   
   ⚠️ **ВАЖНО:** Если Build Command не работает, попробуйте:
   - Убедитесь, что файл `requirements_frontend.txt` есть в корне проекта
   - Или используйте: `pip install fastapi uvicorn jinja2 python-multipart python-dotenv`

6. **Настройте переменные окружения:**
   - Перейдите в "Variables" frontend сервиса
   - Добавьте:
     ```
     API_BASE_URL=https://your-backend-ngrok-url.ngrok.io/api
     ```
   - ⚠️ Замените `your-backend-ngrok-url` на реальный URL из ngrok!

7. **Дождитесь деплоя и скопируйте frontend URL** (например: `https://your-frontend.railway.app`)

---

## Шаг 3: Обновление Backend CORS

1. **Обновите `backend/.env`:**
   ```env
   FRONTEND_URL=https://your-frontend.railway.app
   ```
   ⚠️ Замените на реальный URL frontend из Railway!

2. **Перезапустите backend** (Ctrl+C и снова `python main.py`)

---

## Шаг 4: Проверка

1. **Проверьте Backend:**
   - Откройте `https://your-backend-ngrok-url.ngrok.io/health`
   - Должен вернуться: `{"status":"ok"}`

2. **Проверьте Frontend:**
   - Откройте `https://your-frontend.railway.app/login`
   - Должна открыться страница входа

3. **Проверьте подключение:**
   - Попробуйте зарегистрироваться или войти
   - Если все работает - готово! ✅

---

## Важные замечания

### Backend должен быть запущен

⚠️ **ВАЖНО:** Backend должен работать локально и ngrok туннель должен быть активен!

Если вы остановите backend или ngrok:
- Frontend на Railway не сможет подключиться к backend
- Сайт перестанет работать

### Обновление ngrok URL

Если вы перезапустите ngrok, URL изменится:
1. Обновите `API_BASE_URL` в Railway frontend переменных
2. Перезапустите frontend сервис в Railway

### Постоянный ngrok URL (опционально)

Если хотите постоянный URL для backend:
1. Зарегистрируйтесь на https://dashboard.ngrok.com
2. Получите authtoken
3. Настройте постоянный домен
4. Используйте: `ngrok http 8000 --domain=your-domain.ngrok.io`

---

## Структура

```
Локальный компьютер:
├── Backend (localhost:8000)
│   └── ngrok туннель → https://backend.ngrok.io
│
└── База данных (ngrok)
    └── PostgreSQL через ngrok

Railway:
└── Frontend
    └── https://frontend.railway.app
    └── Подключается к → https://backend.ngrok.io/api
```

---

## Решение проблем

### Frontend не может подключиться к Backend

1. Проверьте, что backend запущен локально
2. Проверьте, что ngrok туннель активен
3. Проверьте `API_BASE_URL` в Railway переменных
4. Проверьте URL: `https://your-backend-ngrok-url.ngrok.io/health`

### CORS ошибки

1. Проверьте `FRONTEND_URL` в `backend/.env`
2. Убедитесь, что URL точно совпадает с Railway frontend URL
3. Перезапустите backend после изменения `.env`

### База данных не подключается

1. Проверьте, что ngrok туннель для PostgreSQL активен
2. Проверьте `DATABASE_URL` в `backend/.env`
3. Проверьте логи backend для деталей ошибки

---

## Автоматизация (опционально)

Можно создать скрипт для автоматического запуска всего:

```powershell
# start_backend_with_ngrok.ps1
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py"
Start-Sleep -Seconds 3
.\start_ngrok_backend.ps1
```

---

## Полезные ссылки

- Railway Dashboard: https://railway.app/dashboard
- ngrok Dashboard: https://dashboard.ngrok.com
- Railway Docs: https://docs.railway.app

