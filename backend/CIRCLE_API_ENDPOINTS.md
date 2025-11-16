# Circle API Endpoints

## Обзор

Новые endpoints для получения информации из Circle API и модификации данных CEO, департаментов и работников.

---

## Circle API Endpoints

### 1. Получить баланс кошелька CEO (USDC)

**GET** `/api/circle/wallet/balance`

**Описание:** Получает баланс USDC для кошелька CEO из Circle API.

**Ответ:**
```json
{
  "wallet_id": "uuid",
  "balance": 1000.50,
  "currency": "USDC"
}
```

**Ошибки:**
- `404` - Company not found
- `400` - Circle wallet ID not configured
- `500` - Failed to get wallet balance

---

### 2. Получить информацию о кошельке CEO

**GET** `/api/circle/wallet/info`

**Описание:** Получает полную информацию о кошельке CEO (адрес, состояние, wallet set ID).

**Ответ:**
```json
{
  "wallet_id": "uuid",
  "address": "0x1234...5678",
  "state": "LIVE",
  "wallet_set_id": "uuid"
}
```

**Ошибки:**
- `404` - Company not found
- `400` - Circle wallet ID not configured
- `500` - Failed to get wallet info

---

### 3. Получить все балансы токенов кошелька CEO

**GET** `/api/circle/wallet/balances`

**Описание:** Получает все балансы токенов для кошелька CEO.

**Ответ:**
```json
{
  "wallet_id": "uuid",
  "balances": [
    {
      "token_id": "uuid",
      "token_address": "0x...",
      "symbol": "USDC",
      "amount": "1000.50",
      "decimals": 6
    }
  ]
}
```

**Ошибки:**
- `404` - Company not found
- `400` - Circle wallet ID not configured
- `500` - Failed to get wallet balances

---

### 4. Получить статус транзакции

**GET** `/api/circle/transaction/{transaction_id}`

**Описание:** Получает статус транзакции из Circle API по transaction ID.

**Параметры:**
- `transaction_id` (path) - UUID транзакции Circle

**Ответ:**
```json
{
  "transaction_id": "uuid",
  "state": "COMPLETE",
  "tx_hash": "0x1234...5678",
  "data": {...}
}
```

**Возможные состояния:**
- `INITIATED` - Транзакция инициирована
- `QUEUED` - Транзакция в очереди
- `SENT` - Транзакция отправлена
- `CONFIRMED` - Транзакция подтверждена
- `COMPLETE` - Транзакция завершена
- `FAILED` - Транзакция провалилась

**Ошибки:**
- `404` - Company not found / Transaction not found
- `500` - Failed to get transaction status

---

### 5. Получить публичный ключ Circle

**GET** `/api/circle/public-key`

**Описание:** Получает публичный ключ Circle для шифрования entity secret (полезно для frontend).

**Ответ:**
```json
{
  "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
  "algorithm": "RSA OAEP with SHA-256"
}
```

**Ошибки:**
- `500` - Failed to get Circle public key

---

## Модификация данных

### CEO (Company) - Обновление

**PUT** `/api/company/master-wallet`

**Описание:** Обновляет данные CEO (кошелек, Circle wallet ID, entity secret, дата/время payroll).

**Тело запроса:**
```json
{
  "master_wallet_address": "0x1234...5678",  // Опционально
  "circle_wallet_id": "uuid",                 // Опционально
  "circle_wallet_set_id": "uuid",             // Опционально
  "entity_secret": "64 hex characters",        // Опционально (будет зашифрован)
  "payroll_date": "2024-01-15",               // Опционально (YYYY-MM-DD)
  "payroll_time": "09:00"                      // Опционально (HH:MM, 24-hour format)
}
```

**Ответ:** `CompanyResponse`

**Ошибки:**
- `404` - Company not found
- `400` - Invalid wallet address format / Invalid entity secret / Invalid payroll time format
- `500` - Failed to encrypt entity secret

---

### Департамент - Обновление

**PUT** `/api/departments/{department_id}`

**Описание:** Обновляет название департамента.

**Параметры:**
- `department_id` (path) - ID департамента

**Тело запроса:**
```json
{
  "name": "Новое название"  // Опционально
}
```

**Ответ:** `DepartmentResponse`

**Ошибки:**
- `404` - Company not found / Department not found
- `400` - Department name cannot be empty

---

### Работник - Обновление

**PUT** `/api/workers/{worker_id}`

**Описание:** Обновляет данные работника.

**Параметры:**
- `worker_id` (path) - ID работника

**Тело запроса:**
```json
{
  "name": "Иван",                    // Опционально
  "surname": "Иванов",               // Опционально
  "salary": 5000.0,                  // Опционально
  "wallet_address": "0x1234...5678", // Опционально
  "is_active": true,                  // Опционально
  "department_id": 1                 // Опционально
}
```

**Ответ:** `WorkerResponse`

**Ошибки:**
- `404` - Company not found / Worker not found / Department not found
- `400` - Invalid wallet address format

---

## Примеры использования

### Получить баланс CEO кошелька

```bash
curl -X GET "http://localhost:8000/api/circle/wallet/balance" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Обновить данные CEO

```bash
curl -X PUT "http://localhost:8000/api/company/master-wallet" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "circle_wallet_id": "your-wallet-uuid",
    "payroll_date": "2024-01-15",
    "payroll_time": "09:00"
  }'
```

### Обновить департамент

```bash
curl -X PUT "http://localhost:8000/api/departments/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новый отдел"
  }'
```

### Обновить работника

```bash
curl -X PUT "http://localhost:8000/api/workers/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "salary": 6000.0,
    "wallet_address": "0x1234567890123456789012345678901234567890"
  }'
```

---

## Аутентификация

Все endpoints требуют JWT токен в заголовке:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

Получить токен можно через `/api/auth/login`.

