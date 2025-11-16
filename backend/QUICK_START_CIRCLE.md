# Быстрый старт: Circle API интеграция

## Шаг 1: Обновить базу данных

Выполните SQL скрипт:
```powershell
cd backend
# Если используете PostgreSQL через psql:
psql -h 5.tcp.eu.ngrok.io -p 14257 -U postgres -d bossboard -f update_schema_for_circle.sql

# Или через Python:
py -c "from src.database import engine, Base; from src.models import *; Base.metadata.create_all(bind=engine)"
```

## Шаг 2: Настроить .env

Добавьте в `backend/.env`:
```env
CIRCLE_API_KEY=TEST_API_KEY:your_key_id:your_key_secret
ENTITY_SECRET=your_64_hex_characters_entity_secret
USDC_TOKEN_ID=your_usdc_token_id  # Опционально
```

## Шаг 3: Установить зависимости

```powershell
pip install -r backend/requirements.txt
```

## Шаг 4: Настроить Circle Wallet

Через API или веб-интерфейс:
- Circle Wallet ID (UUID)
- Master Wallet Address (для отображения)
- Payroll Date (дата зарплаты)
- Payroll Time (время зарплаты, например "09:00")

## Шаг 5: Запустить backend

```powershell
cd backend
python main.py
```

Вы должны увидеть:
```
[APP] Payroll scheduler started - checking every minute
```

## Готово!

- Зарплаты будут отправляться автоматически в заданное время
- Баланс кошелька отображается в Dashboard
- Все транзакции сохраняются в историю

## Проверка

1. Откройте Dashboard - должен отображаться баланс USDC
2. Проверьте настройки компании - должны быть заполнены Circle wallet данные
3. Дождитесь времени зарплаты или выполните вручную через API

