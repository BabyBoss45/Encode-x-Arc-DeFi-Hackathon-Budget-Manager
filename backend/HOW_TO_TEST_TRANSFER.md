# Как протестировать транзакцию USDC

## Параметры тестовой транзакции

- **Sender Wallet ID:** `a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7`
- **Receiver Address:** `0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb`
- **Amount:** `1.0` USDC
- **Blockchain:** `ARC-TESTNET`

## Настройка

### 1. Установите переменные окружения в `backend/.env`:

```env
CIRCLE_API_KEY=TEST_API_KEY:your_actual_api_key_here
ENTITY_SECRET=your_64_character_hex_secret_here
USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8
```

**Где найти:**
- `CIRCLE_API_KEY` - в Circle Dashboard → API Keys
- `ENTITY_SECRET` - в Circle Dashboard → Developer Settings (64 hex символа)
- `USDC_TOKEN_ID` - опционально, можно найти через API или использовать по умолчанию

### 2. Запустите тест:

```bash
cd backend
python test_transfer_demo.py
```

## Альтернатива: через API endpoint

Если backend сервер запущен:

1. **Залогиньтесь:**
```bash
POST http://localhost:8000/api/auth/login
Body: {"email": "your@email.com", "password": "your_password"}
```

2. **Обновите wallet ID компании:**
```bash
PUT http://localhost:8000/api/company/master-wallet
Headers: Authorization: Bearer YOUR_JWT_TOKEN
Body: {
  "circle_wallet_id": "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
}
```

3. **Выполните payroll (который создаст транзакцию):**
```bash
POST http://localhost:8000/api/payroll/execute
Headers: Authorization: Bearer YOUR_JWT_TOKEN
Body: {
  "period_start": "2024-01-01",
  "period_end": "2024-01-31"
}
```

## Проверка статуса транзакции

После создания транзакции, проверьте её статус:

```bash
GET http://localhost:8000/api/circle/transaction/{transaction_id}
Headers: Authorization: Bearer YOUR_JWT_TOKEN
```

## Код для прямого вызова

```python
from src.circle_api import circle_api

result = circle_api.transfer_usdc(
    entity_secret_hex="your_64_char_hex_secret",
    wallet_id="a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7",
    destination_address="0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb",
    amount="1.0",
    token_id="15dc2b5d-0994-58b0-bf8c-3a0501148ee8",  # опционально
    blockchain="ARC-TESTNET"
)

print(f"Transaction ID: {result['id']}")
print(f"State: {result['state']}")
```

