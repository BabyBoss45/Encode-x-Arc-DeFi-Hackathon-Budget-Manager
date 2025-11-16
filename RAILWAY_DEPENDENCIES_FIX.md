# Исправление проблемы с зависимостями на Railway

## Проблема

Railway не устанавливает зависимости перед запуском frontend, даже если указан Build Command.

## Решения

### Решение 1: Проверьте Build Command (Рекомендуется)

В настройках Railway Frontend сервиса:

1. **Root Directory:** оставьте пустым
2. **Build Command:** `pip install --upgrade pip && pip install -r requirements_frontend.txt`
3. **Start Command:** `cd src && python frontend.py`

### Решение 2: Используйте полный список зависимостей в Build Command

Если `requirements_frontend.txt` не работает, используйте прямой список:

**Build Command:**
```bash
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 jinja2==3.1.2 python-multipart==0.0.6 python-dotenv==1.0.0
```

### Решение 3: Создайте requirements.txt в корне проекта

Railway автоматически ищет `requirements.txt` в корне. Можно создать симлинк или скопировать:

```bash
# В корне проекта создайте файл requirements.txt с содержимым requirements_frontend.txt
```

Или используйте Build Command:
```bash
cp requirements_frontend.txt requirements.txt && pip install -r requirements.txt
```

### Решение 4: Используйте nixpacks.toml

Создайте файл `nixpacks.toml` в корне проекта:

```toml
[phases.setup]
nixPkgs = ["python311", "pip"]

[phases.install]
cmds = ["pip install -r requirements_frontend.txt"]

[start]
cmd = "cd src && python frontend.py"
```

### Решение 5: Проверьте логи Railway

1. Откройте логи Railway
2. Найдите секцию "Build"
3. Проверьте, выполняется ли Build Command
4. Если Build Command не выполняется, Railway может использовать другой механизм

---

## Проверка

После применения решения:

1. Сохраните настройки
2. Railway перезапустит деплой
3. В логах должна быть видна установка:
   ```
   Collecting fastapi
   Downloading fastapi-0.104.1-py3-none-any.whl
   ...
   Successfully installed fastapi-0.104.1 ...
   ```

---

## Если ничего не помогает

Попробуйте создать отдельный сервис с минимальной конфигурацией:

1. Удалите текущий frontend сервис
2. Создайте новый сервис из того же репозитория
3. Railway может автоматически определить Python проект
4. Затем добавьте Build Command вручную

---

## Альтернатива: Использовать Dockerfile

Если Railway не может автоматически установить зависимости, можно создать `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_frontend.txt .
RUN pip install --no-cache-dir -r requirements_frontend.txt

COPY src/ ./src/

CMD ["python", "src/frontend.py"]
```

Но это более сложный вариант.

