# Руководство по деплою проекта

## Варианты хостинга

### ✅ Рекомендуемые (бесплатные/дешевые)

#### 1. **Railway** (Рекомендуется) ⭐
- ✅ Бесплатный tier ($5 кредитов в месяц)
- ✅ Автоматический деплой из GitHub
- ✅ Встроенная PostgreSQL база данных
- ✅ Простая настройка
- ✅ Поддержка Python/FastAPI

#### 2. **Render**
- ✅ Бесплатный tier (с ограничениями)
- ✅ Автоматический деплой из GitHub
- ✅ Встроенная PostgreSQL база данных
- ✅ Простая настройка

#### 3. **Fly.io**
- ✅ Бесплатный tier
- ✅ Быстрый деплой
- ✅ Глобальная сеть

### ⚠️ Альтернативы

#### 4. **Heroku**
- ⚠️ Теперь платный (от $5/месяц)
- ✅ Очень простой деплой
- ✅ Много документации

#### 5. **Vercel** (только для frontend)
- ✅ Бесплатный
- ⚠️ Только статические сайты или serverless функции
- ⚠️ Backend нужно хостить отдельно

---

## Быстрый деплой на Railway (Рекомендуется)

### Шаг 1: Подготовка проекта

1. **Убедитесь, что проект в GitHub репозитории**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/ваш-username/ваш-репозиторий.git
   git push -u origin main
   ```

2. **Создайте файл `Procfile` в корне проекта:**
   ```
   web: cd backend && python main.py
   ```

3. **Создайте `runtime.txt` в корне проекта:**
   ```
   python-3.11
   ```

### Шаг 2: Деплой на Railway

1. **Зарегистрируйтесь на Railway:**
   - Перейдите на https://railway.app
   - Войдите через GitHub

2. **Создайте новый проект:**
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий

3. **Добавьте PostgreSQL базу данных:**
   - В проекте нажмите "+ New"
   - Выберите "Database" → "PostgreSQL"
   - Railway автоматически создаст переменную `DATABASE_URL`

4. **Настройте переменные окружения:**
   - Перейдите в "Variables"
   - Добавьте:
     ```
     DATABASE_URL (автоматически из PostgreSQL)
     JWT_SECRET_KEY=your-secret-key-here
     CIRCLE_API_KEY=your-circle-api-key
     ENTITY_SECRET=your-entity-secret
     USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8
     FRONTEND_URL=https://your-frontend-url.com (если frontend отдельно)
     ```

5. **Настройте команду запуска:**
   - В настройках сервиса укажите:
     - **Start Command:** `cd backend && python main.py`
     - **Root Directory:** `/` (корень проекта)

6. **Деплой:**
   - Railway автоматически задеплоит проект
   - Получите URL вашего backend (например: `https://your-app.railway.app`)

### Шаг 3: Деплой Frontend

**Вариант A: На том же Railway**
- Создайте второй сервис для frontend
- Root Directory: `/src`
- Start Command: `python frontend.py`
- Port: 8001

**Вариант B: На отдельном хостинге**
- Используйте Railway, Render или Vercel для frontend
- Установите переменную `API_BASE_URL=https://your-backend.railway.app/api`

---

## Деплой на Render

### Шаг 1: Подготовка

1. Создайте файл `render.yaml` в корне проекта:
```yaml
services:
  - type: web
    name: backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && python main.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: bossboard-db
          property: connectionString
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: CIRCLE_API_KEY
        sync: false
      - key: ENTITY_SECRET
        sync: false

  - type: web
    name: frontend
    env: python
    buildCommand: pip install -r requirements_frontend.txt
    startCommand: cd src && python frontend.py
    envVars:
      - key: API_BASE_URL
        fromService:
          name: backend
          type: web
          property: host
          suffix: /api

databases:
  - name: bossboard-db
    plan: free
    databaseName: bossboard
    user: bossboard_user
```

### Шаг 2: Деплой

1. Зарегистрируйтесь на https://render.com
2. Подключите GitHub репозиторий
3. Выберите "New Blueprint"
4. Render автоматически создаст все сервисы

---

## Деплой на Fly.io

### Шаг 1: Установка Fly CLI

```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

### Шаг 2: Создание конфигурации

Создайте файл `fly.toml` в корне проекта:

```toml
app = "your-app-name"
primary_region = "iad"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[[services.http_checks]]
  interval = "10s"
  timeout = "2s"
  grace_period = "5s"
  method = "GET"
  path = "/health"
```

### Шаг 3: Деплой

```bash
fly launch
fly postgres create
fly secrets set DATABASE_URL="postgresql://..." JWT_SECRET_KEY="..." CIRCLE_API_KEY="..."
fly deploy
```

---

## GitHub Actions для автоматического деплоя

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      - name: Deploy
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Структура файлов для деплоя

```
.
├── Procfile              # Для Railway/Heroku
├── runtime.txt           # Версия Python
├── render.yaml          # Для Render
├── fly.toml             # Для Fly.io
├── .github/
│   └── workflows/
│       └── deploy.yml   # GitHub Actions
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example     # Пример переменных
└── src/
    ├── frontend.py
    └── .env.example      # Пример переменных
```

---

## Рекомендации

### Для быстрого старта:
1. **Railway** - самый простой и быстрый вариант
2. Используйте встроенную PostgreSQL от Railway
3. Frontend можно задеплоить на том же Railway или отдельно

### Для production:
1. Используйте отдельные сервисы для backend и frontend
2. Настройте CI/CD через GitHub Actions
3. Используйте переменные окружения для секретов
4. Настройте мониторинг и логирование

---

## Полезные ссылки

- Railway: https://railway.app
- Render: https://render.com
- Fly.io: https://fly.io
- Heroku: https://www.heroku.com
- Vercel: https://vercel.com

---

## Решение проблем

### Проблема: Приложение не запускается
- Проверьте логи в панели хостинга
- Убедитесь, что все переменные окружения установлены
- Проверьте, что порт правильный (Railway использует переменную PORT)

### Проблема: База данных не подключается
- Проверьте DATABASE_URL
- Убедитесь, что база данных создана и запущена
- Проверьте, что пароль правильный

### Проблема: Frontend не может подключиться к Backend
- Проверьте CORS настройки в backend
- Убедитесь, что FRONTEND_URL установлен правильно
- Проверьте, что API_BASE_URL указывает на правильный backend URL

