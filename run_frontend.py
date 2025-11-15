#!/usr/bin/env python3
"""
Простой скрипт для запуска фронтенда
Просто запустите этот файл: python run_frontend.py
"""
import sys
import os
import subprocess

# Переходим в папку src
os.chdir(os.path.join(os.path.dirname(__file__), 'src'))

# Проверяем зависимости
try:
    import fastapi
    import uvicorn
    import jinja2
except ImportError:
    print("❌ Не установлены зависимости!")
    print("\n📦 Установите их командой:")
    print("   pip3 install fastapi uvicorn jinja2 python-multipart")
    print("\nИли:")
    print("   python3 -m pip install fastapi uvicorn jinja2 python-multipart")
    print("\nИли:")
    print("   pip3 install -r requirements_frontend.txt")
    sys.exit(1)

# Запускаем фронтенд
print("🚀 Запуск BossBoard Frontend...")
print("📝 Откройте в браузере: http://localhost:8001/login")
print("⏹️  Для остановки нажмите Ctrl+C\n")

try:
    import uvicorn
    uvicorn.run("frontend:app", host="0.0.0.0", port=8001, reload=True)
except KeyboardInterrupt:
    print("\n👋 Остановка сервера...")
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    sys.exit(1)

