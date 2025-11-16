# Скрипт для настройки подключения Frontend на Render к Backend на ngrok

$backendNgrokUrl = "https://frances-hyponastic-belia.ngrok-free.dev"
$frontendRenderUrl = "https://encode-x-arc-defi-hackathon-budget.onrender.com"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Настройка подключения Frontend к Backend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Backend ngrok URL: $backendNgrokUrl" -ForegroundColor Green
Write-Host "Frontend Render URL: $frontendRenderUrl" -ForegroundColor Green
Write-Host ""

# Обновление backend/.env
$envPath = "backend\.env"
if (Test-Path $envPath) {
    Write-Host "Обновление backend/.env..." -ForegroundColor Yellow
    
    $content = Get-Content $envPath
    $updated = $false
    $newContent = @()
    
    foreach ($line in $content) {
        if ($line -match "^FRONTEND_URL=") {
            $newContent += "FRONTEND_URL=$frontendRenderUrl"
            $updated = $true
        } else {
            $newContent += $line
        }
    }
    
    if (-not $updated) {
        $newContent += "FRONTEND_URL=$frontendRenderUrl"
    }
    
    $newContent | Set-Content $envPath
    Write-Host "✓ Обновлен backend/.env: FRONTEND_URL=$frontendRenderUrl" -ForegroundColor Green
} else {
    Write-Host "✗ Файл backend/.env не найден" -ForegroundColor Red
    Write-Host "Создайте файл backend/.env и добавьте:" -ForegroundColor Yellow
    Write-Host "FRONTEND_URL=$frontendRenderUrl" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Что нужно сделать в Render:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Откройте: https://dashboard.render.com" -ForegroundColor Yellow
Write-Host "2. Выберите Frontend сервис" -ForegroundColor Yellow
Write-Host "3. Перейдите в Environment" -ForegroundColor Yellow
Write-Host "4. Добавьте/обновите переменную:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Key: API_BASE_URL" -ForegroundColor White
Write-Host "   Value: $backendNgrokUrl/api" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Сохраните - Render автоматически перезапустит frontend" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "После настройки:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Перезапустите backend (Ctrl+C и снова python main.py)" -ForegroundColor Yellow
Write-Host "2. Проверьте логи backend - должно быть:" -ForegroundColor Yellow
Write-Host "   [CORS] Added frontend URL: $frontendRenderUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Откройте frontend: $frontendRenderUrl" -ForegroundColor Yellow
Write-Host "4. Попробуйте зарегистрироваться или войти" -ForegroundColor Yellow
Write-Host ""

