# Исправление ошибки "ModuleNotFoundError: No module named 'fastapi'"

## Проблема

Railway не устанавливает зависимости перед запуском frontend.

## Решение

В настройках Railway Frontend сервиса (Settings → Deploy):

1. **Root Directory:** оставьте пустым (корень проекта `/`)
2. **Build Command:** `pip install -r requirements_frontend.txt`
3. **Start Command:** `cd src && python frontend.py`

⚠️ **ВАЖНО:** Build Command должен быть установлен! Без него Railway не установит зависимости.

---

## Проверка

После настройки:

1. Сохраните настройки
2. Railway автоматически перезапустит деплой
3. В логах должно быть видно установку зависимостей:
   ```
   Collecting fastapi
   Collecting uvicorn
   ...
   Successfully installed fastapi-...
   ```
4. Затем должен запуститься frontend

---

## Если проблема осталась

1. **Проверьте, что `requirements_frontend.txt` есть в корне проекта**
2. **Проверьте логи Railway** - там будет видно, что происходит при сборке
3. **Убедитесь, что Build Command указан правильно**

---

## Альтернативный вариант: Procfile для frontend

Можно создать отдельный Procfile для frontend (но Railway обычно использует настройки из UI):

```
web: pip install -r requirements_frontend.txt && cd src && python frontend.py
```

Но лучше использовать Build Command в настройках Railway.
