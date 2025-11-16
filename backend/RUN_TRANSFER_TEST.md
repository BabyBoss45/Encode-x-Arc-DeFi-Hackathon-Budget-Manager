# Как запустить тест транзакции

## Способ 1: Через аргумент командной строки (рекомендуется)

```bash
cd backend
python test_transfer_now.py YOUR_64_CHAR_HEX_ENTITY_SECRET
```

Пример:
```bash
python test_transfer_now.py 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

## Способ 2: Через переменную окружения

```bash
cd backend
$env:ENTITY_SECRET="your_64_char_hex"; python test_transfer_now.py
```

Или в PowerShell:
```powershell
$env:ENTITY_SECRET="your_64_char_hex"
python test_transfer_now.py
```

## Способ 3: Добавить в .env файл

1. Откройте `backend/.env`
2. Добавьте строку:
   ```
   ENTITY_SECRET=your_64_character_hex_secret_here
   ```
3. Сохраните файл
4. Запустите:
   ```bash
   python test_transfer_now.py
   ```

## Параметры теста

- **Sender:** `a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7`
- **Receiver:** `0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb`
- **Amount:** `1.0` USDC
- **Blockchain:** `ARC-TESTNET`

## Проверка переменных окружения

Перед запуском теста проверьте настройки:
```bash
python check_env.py
```

