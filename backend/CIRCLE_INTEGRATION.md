# Circle API Integration Guide

## Обзор

Проект интегрирован с Circle Developer-Controlled Wallets API для автоматической отправки зарплат в USDC и отображения баланса кошелька.

## Что было добавлено

### 1. Автоматическая отправка зарплат
- Планировщик проверяет время зарплаты каждую минуту
- Автоматически отправляет USDC всем активным работникам в заданное время
- Сохраняет транзакции в БД с полным статусом

### 2. Отображение баланса кошелька
- Баланс USDC отображается в Dashboard
- Обновляется автоматически при загрузке страницы

### 3. История транзакций
- Все транзакции сохраняются в таблицу `payroll_transactions`
- Статусы транзакций: INITIATED, QUEUED, SENT, CONFIRMED, COMPLETE, failed
- Сохраняется Circle transaction ID и blockchain hash

## Настройка

### 1. Обновить базу данных

Выполните SQL скрипт для добавления новых полей:

```sql
-- Выполните backend/update_schema_for_circle.sql
-- Или используйте миграцию Alembic (если настроена)
```

Или выполните через Python:
```powershell
cd backend
py -c "from src.database import engine, Base; from src.models import *; Base.metadata.create_all(bind=engine)"
```

### 2. Настроить переменные окружения

В файле `backend/.env` добавьте:

```env
# Circle API Configuration
CIRCLE_API_KEY=TEST_API_KEY:your_key_id:your_key_secret
ENTITY_SECRET=your_64_character_hex_entity_secret
USDC_TOKEN_ID=your_usdc_token_id  # Optional: для ARC-TESTNET
```

**Важно:**
- `ENTITY_SECRET` должен быть 64 hex символа
- `CIRCLE_API_KEY` должен быть в формате `TEST_API_KEY:KEY_ID:KEY_SECRET`
- `USDC_TOKEN_ID` можно найти через Circle API или использовать token address

### 3. Настроить компанию через API

Используйте API endpoint для настройки Circle wallet:

```bash
PUT /api/company/master-wallet
{
  "master_wallet_address": "0x...",  # Blockchain address (для отображения)
  "circle_wallet_id": "uuid-here",   # Circle wallet ID (UUID)
  "circle_wallet_set_id": "uuid-here",  # Optional: wallet set ID
  "entity_secret": "64_hex_chars",   # Будет зашифрован и сохранен
  "payroll_date": "2025-01-15",     # Дата зарплаты (YYYY-MM-DD)
  "payroll_time": "09:00"            # Время зарплаты (HH:MM, 24-часовой формат)
}
```

Или через веб-интерфейс в разделе настроек компании.

## Использование

### Автоматическая отправка зарплат

1. Настройте `payroll_date` и `payroll_time` в настройках компании
2. Убедитесь, что Circle wallet настроен и имеет достаточный баланс USDC
3. Планировщик автоматически проверит время и отправит зарплаты

**Как это работает:**
- Планировщик запускается каждую минуту
- Проверяет все компании с настроенным временем зарплаты
- Если текущая дата и время совпадают с настройками → отправляет зарплаты
- Предотвращает повторную отправку в тот же день

### Ручная отправка зарплат

Используйте API endpoint:

```bash
POST /api/payroll/execute
{
  "period_start": "2025-01-01",
  "period_end": "2025-01-31"
}
```

### Просмотр транзакций

```bash
GET /api/payroll/transactions
```

Возвращает список всех транзакций с статусами:
- `pending` - создана, но не отправлена
- `INITIATED` - транзакция создана в Circle
- `QUEUED` - в очереди на отправку
- `SENT` - отправлена в блокчейн
- `CONFIRMED` - подтверждена в блокчейне
- `COMPLETE` - завершена успешно
- `failed` - ошибка при отправке

## Структура данных

### Company (обновлено)
- `master_wallet_address` - адрес кошелька для отображения
- `circle_wallet_id` - Circle wallet ID (UUID) для API вызовов
- `circle_wallet_set_id` - Circle wallet set ID
- `entity_secret_encrypted` - зашифрованный entity secret (base64)
- `payroll_date` - дата зарплаты
- `payroll_time` - время зарплаты (HH:MM)

### PayrollTransaction (обновлено)
- `circle_transaction_id` - Circle transaction ID (UUID)
- `transaction_hash` - Blockchain transaction hash (когда доступен)
- `status` - статус транзакции (поддерживает Circle states)

## Безопасность

1. **Entity Secret:**
   - Хранится в зашифрованном виде в БД
   - Рекомендуется использовать переменные окружения (`ENTITY_SECRET`)
   - Шифруется перед каждым API вызовом с помощью RSA OAEP

2. **API Keys:**
   - Никогда не коммитьте `.env` файл
   - Используйте разные ключи для dev/prod

3. **Баланс:**
   - Проверяется перед отправкой зарплат
   - Предотвращает отправку при недостаточном балансе

## Troubleshooting

### Ошибка: "Circle wallet ID not set"
**Решение:** Настройте Circle wallet через API или веб-интерфейс

### Ошибка: "Entity secret not found"
**Решение:** Установите `ENTITY_SECRET` в `.env` или передайте через API

### Ошибка: "Insufficient wallet balance"
**Решение:** Пополните Circle wallet USDC через Circle faucet или другой источник

### Транзакции не отправляются автоматически
**Проверьте:**
1. Планировщик запущен (должно быть сообщение при старте backend)
2. `payroll_date` и `payroll_time` настроены правильно
3. Текущая дата/время совпадают с настройками
4. Зарплата еще не была отправлена сегодня

### Баланс не отображается в Dashboard
**Проверьте:**
1. Circle wallet ID настроен
2. Circle API ключ правильный
3. Кошелек имеет USDC токены

## API Endpoints

### Company
- `GET /api/company/` - получить информацию о компании
- `PUT /api/company/master-wallet` - обновить настройки кошелька и зарплаты

### Payroll
- `POST /api/payroll/execute` - выполнить зарплату вручную
- `GET /api/payroll/transactions` - получить историю транзакций

### Dashboard
- `GET /api/dashboard/stats` - получить статистику (включая баланс кошелька)

## Зависимости

Убедитесь, что установлены:
```bash
pip install -r backend/requirements.txt
```

Основные зависимости для Circle API:
- `requests>=2.31.0`
- `cryptography>=41.0.0` - для RSA шифрования
- `apscheduler>=3.10.4` - для планировщика

## Дополнительные ресурсы

- [Circle Developer Documentation](https://developers.circle.com/wallets/dev-controlled/create-your-first-wallet)
- [Circle API Reference](https://developers.circle.com/api-reference)
- [Circle Console](https://console.circle.com)

