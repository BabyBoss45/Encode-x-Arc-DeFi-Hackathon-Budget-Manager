# Быстрый деплой на Railway

## За 5 минут задеплоить проект

### Шаг 1: Подготовка GitHub репозитория

1. **Создайте репозиторий на GitHub** (если еще нет)
2. **Закоммитьте проект:**
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git remote add origin https://github.com/ваш-username/ваш-репозиторий.git
   git push -u origin main
   ```

### Шаг 2: Регистрация на Railway

1. Перейдите на https://railway.app
2. Нажмите "Start a New Project"
3. Войдите через GitHub
4. Выберите "Deploy from GitHub repo"
5. Выберите ваш репозиторий

### Шаг 3: Настройка Backend

1. **Railway автоматически определит Python проект**

2. **Добавьте PostgreSQL:**
   - Нажмите "+ New" в проекте
   - Выберите "Database" → "PostgreSQL"
   - Railway создаст переменную `DATABASE_URL` автоматически

3. **Настройте переменные окружения:**
   - Перейдите в "Variables" вашего сервиса
   - Добавьте:
     ```
     JWT_SECRET_KEY=your-secret-key-min-32-chars
     CIRCLE_API_KEY=your-circle-api-key
     ENTITY_SECRET=your-64-char-hex-secret
     USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8
     ```
   - `DATABASE_URL` уже будет установлен автоматически

4. **Настройте команду запуска:**
   - В настройках сервиса (Settings → Deploy)
   - **Start Command:** `cd backend && python main.py`
   - **Root Directory:** оставьте пустым (корень проекта)

5. **Деплой:**
   - Railway автоматически задеплоит проект
   - Дождитесь завершения деплоя
   - Получите URL (например: `https://your-app.railway.app`)

### Шаг 4: Настройка Frontend

**Вариант A: На том же Railway (рекомендуется)**

1. **Создайте новый сервис:**
   - В проекте нажмите "+ New" → "GitHub Repo"
   - Выберите тот же репозиторий

2. **Настройте:**
   - **Root Directory:** `/src`
   - **Start Command:** `python frontend.py`
   - **Port:** 8001 (или оставьте автоматический)

3. **Добавьте переменную окружения:**
   - `API_BASE_URL=https://your-backend.railway.app/api`
   - Замените `your-backend` на реальный URL вашего backend

4. **Обновите Backend CORS:**
   - В переменных окружения backend добавьте:
   - `FRONTEND_URL=https://your-frontend.railway.app`
   - Замените на реальный URL frontend

**Вариант B: Отдельный хостинг**

Frontend можно задеплоить на:
- Render (бесплатно)
- Vercel (бесплатно, но только статический или serverless)
- Другой Railway проект

### Шаг 5: Проверка

1. **Проверьте Backend:**
   - Откройте `https://your-backend.railway.app/health`
   - Должен вернуться: `{"status":"ok"}`

2. **Проверьте Frontend:**
   - Откройте `https://your-frontend.railway.app/login`
   - Должна открыться страница входа

3. **Проверьте базу данных:**
   - В Railway перейдите в PostgreSQL сервис
   - Используйте встроенный PostgreSQL Browser для проверки таблиц

---

## Важные замечания

### Порт

Railway автоматически устанавливает переменную `PORT`. Если нужно использовать другой порт, обновите `backend/main.py`:

```python
import os
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### Переменные окружения

⚠️ **Никогда не коммитьте `.env` файлы!**
- Используйте Railway Variables для секретов
- `.env` файлы должны быть в `.gitignore`

### База данных

Railway автоматически создает `DATABASE_URL`. Убедитесь, что:
- PostgreSQL сервис запущен
- Переменная `DATABASE_URL` установлена в backend сервисе

### CORS

Убедитесь, что `FRONTEND_URL` в backend переменных окружения указывает на правильный frontend URL.

---

## Автоматический деплой

Railway автоматически деплоит при каждом push в GitHub:
- Просто сделайте `git push`
- Railway автоматически обновит приложение

---

## Мониторинг

- **Логи:** Просматривайте в реальном времени в Railway dashboard
- **Метрики:** CPU, память, сеть доступны в панели
- **База данных:** Используйте встроенный PostgreSQL Browser

---

## Обновление

1. Внесите изменения в код
2. Закоммитьте: `git commit -am "Update"`
3. Запушьте: `git push`
4. Railway автоматически задеплоит новую версию

---

## Решение проблем

### Приложение не запускается
- Проверьте логи в Railway dashboard
- Убедитесь, что все переменные окружения установлены
- Проверьте, что команда запуска правильная

### База данных не подключается
- Проверьте, что PostgreSQL сервис запущен
- Убедитесь, что `DATABASE_URL` установлен в backend сервисе
- Проверьте логи для деталей ошибки

### Frontend не может подключиться к Backend
- Проверьте `API_BASE_URL` в frontend переменных
- Проверьте `FRONTEND_URL` в backend переменных
- Убедитесь, что CORS настроен правильно

---

## Полезные ссылки

- Railway Docs: https://docs.railway.app
- Railway Dashboard: https://railway.app/dashboard
- Support: https://railway.app/support

