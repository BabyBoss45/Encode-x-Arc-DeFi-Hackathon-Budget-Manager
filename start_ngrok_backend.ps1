# PowerShell script to start ngrok tunnel for backend (port 8000)
# Backend будет доступен через ngrok, frontend на Railway

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ngrok tunnel for BACKEND" -ForegroundColor Cyan
Write-Host "Port: 8000" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok is installed
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host "ERROR: ngrok is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install ngrok:" -ForegroundColor Yellow
    Write-Host "1. Download from https://ngrok.com/download" -ForegroundColor White
    Write-Host "2. Extract ngrok.exe to a folder in your PATH" -ForegroundColor White
    Write-Host "3. Or add ngrok.exe location to PATH environment variable" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run ngrok directly:" -ForegroundColor Yellow
    Write-Host "  ngrok http 8000" -ForegroundColor White
    exit 1
}

Write-Host "Starting ngrok tunnel..." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Copy the 'Forwarding' URL (e.g., https://xxxx-xx-xx-xx-xx.ngrok.io)" -ForegroundColor Yellow
Write-Host ""
Write-Host "You will need to:" -ForegroundColor Yellow
Write-Host "1. Set API_BASE_URL in Railway frontend variables:" -ForegroundColor White
Write-Host "   API_BASE_URL=https://your-backend-ngrok-url.ngrok.io/api" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Set FRONTEND_URL in backend .env file:" -ForegroundColor White
Write-Host "   FRONTEND_URL=https://your-frontend.railway.app" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop ngrok" -ForegroundColor Gray
Write-Host ""

# Start ngrok
ngrok http 8000

