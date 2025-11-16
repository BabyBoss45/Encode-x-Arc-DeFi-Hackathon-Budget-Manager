# Быстрый деплой на Railway

## Архитектура

- ✅ **Backend** - работает локально, доступен через ngrok
- ✅ **База данных** - PostgreSQL на ngrok (как настроено)
- ✅ **Frontend** - деплоится на Railway

---

## Быстрый старт

### Шаг 1: Запуск Backend с ngrok

1. **Запустите backend локально:**
   ```powershell
   cd backend
   python main.py
   ```

2. **В другом терминале запустите ngrok:**
   ```powershell
   .\start_ngrok_backend.ps1
   ```

3. **Скопируйте backend ngrok URL** (например: `https://abc123.ngrok.io`)

### Шаг 2: Деплой Frontend на Railway

1. **Перейдите на https://railway.app**
2. **Войдите через GitHub**
3. **Создайте новый проект:**
   - Нажмите "Start a New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий

4. **Настройте Frontend сервис:**
   - **Root Directory:** оставьте пустым (корень проекта)
   - **Build Command:** `pip install -r requirements_frontend.txt`
   - **Start Command:** `cd src && python frontend.py`

5. **Настройте переменные окружения:**
   - Перейдите в "Variables"
   - Добавьте:
     ```
     API_BASE_URL=https://your-backend-ngrok-url.ngrok.io/api
     ```
   - ⚠️ Замените на реальный URL из ngrok!

6. **Дождитесь деплоя и скопируйте frontend URL**

### Шаг 3: Обновление Backend CORS

1. **Обновите `backend/.env`:**
   ```env
   FRONTEND_URL=https://your-frontend.railway.app
   ```

2. **Перезапустите backend**

---

## Проверка

- Backend: `https://your-backend-ngrok-url.ngrok.io/health`
- Frontend: `https://your-frontend.railway.app/login`

---

📖 **Подробная инструкция:** См. `DEPLOY_FRONTEND_RAILWAY.md`
