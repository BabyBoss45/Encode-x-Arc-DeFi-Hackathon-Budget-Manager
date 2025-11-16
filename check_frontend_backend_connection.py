#!/usr/bin/env python3
"""
Проверка подключения Frontend к Backend
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

print("=" * 60)
print("Проверка подключения Frontend к Backend")
print("=" * 60)

# Получаем настройки
backend_ngrok_url = input("\nВведите Backend ngrok URL (например: https://frances-hyponastic-belia.ngrok-free.dev): ").strip()
frontend_render_url = input("Введите Frontend Render URL (например: https://your-app.onrender.com): ").strip()

if not backend_ngrok_url or not frontend_render_url:
    print("\nОшибка: Нужно указать оба URL")
    exit(1)

print("\n" + "=" * 60)
print("Проверка Backend")
print("=" * 60)

# Проверка backend локально
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    if response.status_code == 200:
        print("✓ Backend доступен локально: http://localhost:8000/health")
    else:
        print(f"✗ Backend отвечает с кодом {response.status_code}")
except Exception as e:
    print(f"✗ Backend недоступен локально: {e}")
    print("  Убедитесь, что backend запущен: cd backend && python main.py")

# Проверка backend через ngrok
try:
    health_url = f"{backend_ngrok_url}/health"
    response = requests.get(health_url, timeout=5)
    if response.status_code == 200:
        print(f"✓ Backend доступен через ngrok: {health_url}")
        print(f"  Ответ: {response.json()}")
    else:
        print(f"✗ Backend отвечает с кодом {response.status_code}")
except Exception as e:
    print(f"✗ Backend недоступен через ngrok: {e}")

print("\n" + "=" * 60)
print("Проверка Frontend")
print("=" * 60)

# Проверка frontend
try:
    response = requests.get(frontend_render_url, timeout=10, allow_redirects=True)
    if response.status_code == 200:
        print(f"✓ Frontend доступен: {frontend_render_url}")
    else:
        print(f"✗ Frontend отвечает с кодом {response.status_code}")
except Exception as e:
    print(f"✗ Frontend недоступен: {e}")

print("\n" + "=" * 60)
print("Проверка настроек")
print("=" * 60)

# Проверка backend .env
env_path = "backend/.env"
if os.path.exists(env_path):
    load_dotenv(env_path)
    frontend_url_env = os.getenv("FRONTEND_URL")
    if frontend_url_env:
        print(f"✓ FRONTEND_URL в backend/.env: {frontend_url_env}")
        if frontend_url_env == frontend_render_url:
            print("  ✓ URL совпадает с Render frontend URL")
        else:
            print(f"  ✗ URL НЕ совпадает! Ожидается: {frontend_render_url}")
            print(f"     Обновите backend/.env: FRONTEND_URL={frontend_render_url}")
    else:
        print("✗ FRONTEND_URL не найден в backend/.env")
        print(f"  Добавьте: FRONTEND_URL={frontend_render_url}")
else:
    print(f"✗ Файл {env_path} не найден")

print("\n" + "=" * 60)
print("Рекомендации")
print("=" * 60)

print("\n1. В Render Frontend Environment Variables должно быть:")
print(f"   API_BASE_URL={backend_ngrok_url}/api")

print("\n2. В backend/.env должно быть:")
print(f"   FRONTEND_URL={frontend_render_url}")

print("\n3. После изменения backend/.env перезапустите backend")

print("\n4. Проверьте логи backend - должно быть:")
print(f"   [CORS] Added frontend URL: {frontend_render_url}")

print("\n" + "=" * 60)

