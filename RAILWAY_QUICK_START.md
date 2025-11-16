# Быстрый деплой на Railway

## За 5 минут задеплоить Frontend и Backend

### Шаг 1: Подготовка GitHub репозитория

1. **Создайте репозиторий на GitHub** (если еще нет)
2. **Закоммитьте проект:**
   ```bash
   git init
   git add .
   git commit -m "Ready for Railway deployment"
   git remote add origin https://github.com/ваш-username/ваш-репозиторий.git
   git push -u origin main
   ```

### Шаг 2: Деплой Backend на Railway

1. **Перейдите на https://railway.app**
2. **Войдите через GitHub**
3. **Создайте новый проект:**
   - Нажмите "Start a New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий

4. **Railway автоматически создаст сервис для backend**

5. **Настройте переменные окружения:**
   - Перейдите в "Variables" вашего сервиса
   - Добавьте:
     ```
     DATABASE_URL=postgresql://postgres:admin@ваш-ngrok-хост:порт/bossboard
     JWT_SECRET_KEY=your-secret-key-min-32-chars
     CIRCLE_API_KEY=your-circle-api-key
     ENTITY_SECRET=your-64-char-hex-secret
     USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8
     ```
   - ⚠️ **ВАЖНО:** Используйте ваш существующий DATABASE_URL с ngrok!

6. **Настройте команду запуска:**
   - В настройках сервиса (Settings → Deploy)
   - **Start Command:** `cd backend && python main.py`
   - **Root Directory:** оставьте пустым

7. **Дождитесь деплоя и скопируйте URL backend** (например: `https://your-backend.railway.app`)

### Шаг 3: Деплой Frontend на Railway

1. **В том же проекте Railway нажмите "+ New"**
2. **Выберите "GitHub Repo"**
3. **Выберите тот же репозиторий**

4. **Настройте Frontend сервис:**
   - **Root Directory:** `/src`
   - **Start Command:** `python frontend.py`

5. **Настройте переменные окружения:**
   - Перейдите в "Variables" frontend сервиса
   - Добавьте:
     ```
     API_BASE_URL=https://your-backend.railway.app/api
     ```
   - ⚠️ Замените `your-backend` на реальный URL вашего backend!

6. **Обновите Backend CORS:**
   - Вернитесь в backend сервис
   - В "Variables" добавьте:
     ```
     FRONTEND_URL=https://your-frontend.railway.app
     ```
   - ⚠️ Замените `your-frontend` на реальный URL вашего frontend!

7. **Дождитесь деплоя**

### Шаг 4: Проверка

1. **Проверьте Backend:**
   - Откройте `https://your-backend.railway.app/health`
   - Должен вернуться: `{"status":"ok"}`

2. **Проверьте Frontend:**
   - Откройте `https://your-frontend.railway.app/login`
   - Должна открыться страница входа

3. **Проверьте подключение:**
   - Попробуйте зарегистрироваться или войти
   - Если все работает - готово! ✅

---

## Структура проекта на Railway

```
Railway Project
├── Backend Service
│   ├── Root: / (корень проекта)
│   ├── Start Command: cd backend && python main.py
│   └── Variables:
│       ├── DATABASE_URL (ваш ngrok)
│       ├── JWT_SECRET_KEY
│       ├── CIRCLE_API_KEY
│       ├── ENTITY_SECRET
│       ├── USDC_TOKEN_ID
│       └── FRONTEND_URL
│
└── Frontend Service
    ├── Root: /src
    ├── Start Command: python frontend.py
    └── Variables:
        └── API_BASE_URL
```

---

## Автоматическое обновление

Railway автоматически обновляет проект при каждом push в GitHub:
- Просто сделайте `git push`
- Railway автоматически задеплоит новую версию

---

## Решение проблем

### Backend не запускается
- Проверьте логи в Railway dashboard
- Убедитесь, что все переменные окружения установлены
- Проверьте, что DATABASE_URL правильный (ваш ngrok)

### Frontend не может подключиться к Backend
- Проверьте `API_BASE_URL` в frontend переменных
- Проверьте `FRONTEND_URL` в backend переменных
- Убедитесь, что оба сервиса запущены

### База данных не подключается
- Проверьте, что ngrok туннель для PostgreSQL активен
- Убедитесь, что DATABASE_URL правильный
- Проверьте логи backend для деталей ошибки

---

## Полезные ссылки

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- Support: https://railway.app/support

