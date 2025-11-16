"""
Test wallet balance via our backend API
Requires authentication token
"""
import requests
import json

# Configuration
API_BASE = "http://localhost:8000"
WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"

print("=" * 80)
print("TESTING VIA BACKEND API")
print("=" * 80)
print(f"API Base: {API_BASE}")
print(f"Wallet ID: {WALLET_ID}")
print()

# Check if server is running
print("[CHECK] Checking if backend server is running...")
try:
    response = requests.get(f"{API_BASE}/health", timeout=2)
    if response.status_code == 200:
        print("[OK] Backend server is running")
    else:
        print(f"[WARNING] Server responded with status {response.status_code}")
except Exception as e:
    print(f"[ERROR] Backend server is not running: {e}")
    print("Please start the backend server first:")
    print("  cd backend")
    print("  python main.py")
    exit(1)

print()

# Note: This requires authentication
print("[INFO] To test wallet balance via API, you need:")
print("  1. Login to get JWT token:")
print(f"     POST {API_BASE}/api/auth/login")
print("     Body: {\"email\": \"your@email.com\", \"password\": \"your_password\"}")
print()
print("  2. Then call:")
print(f"     GET {API_BASE}/api/circle/wallet/balance")
print("     Header: Authorization: Bearer YOUR_JWT_TOKEN")
print()
print("  3. Or update company wallet ID first:")
print(f"     PUT {API_BASE}/api/company/master-wallet")
print("     Body: {\"circle_wallet_id\": \"" + WALLET_ID + "\"}")
print()

# Try to test Circle API directly with better error handling
print("=" * 80)
print("TESTING CIRCLE API DIRECTLY")
print("=" * 80)

import os
from dotenv import load_dotenv
load_dotenv()

api_key_raw = os.getenv("CIRCLE_API_KEY", "").strip()
if api_key_raw:
    print(f"[INFO] API Key found: {api_key_raw[:20]}...")
    
    # Try different API key formats
    api_keys_to_try = [
        api_key_raw,
        f"TEST_API_KEY:{api_key_raw}",
        api_key_raw if api_key_raw.count(":") == 2 else None
    ]
    
    for idx, api_key in enumerate(api_keys_to_try, 1):
        if not api_key:
            continue
            
        print()
        print(f"[TEST {idx}] Trying API key format...")
        print(f"Format: {'TEST_API_KEY:key' if api_key.count(':') == 2 else 'key'}")
        
        try:
            url = f"https://api.circle.com/v1/w3s/developer/wallets/{WALLET_ID}/balances"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                token_balances = result.get("data", {}).get("tokenBalances", [])
                print(f"[SUCCESS] Found {len(token_balances)} token balance(s)")
                
                for tb in token_balances:
                    token = tb.get("token", {})
                    print(f"  - {token.get('symbol')}: {tb.get('amount')}")
                break
            elif response.status_code == 401:
                print("[ERROR] Unauthorized - Invalid API key")
            elif response.status_code == 404:
                print("[ERROR] Wallet not found - Check wallet ID")
            else:
                print(f"[ERROR] {response.text}")
        except Exception as e:
            print(f"[ERROR] {e}")
else:
    print("[ERROR] CIRCLE_API_KEY not found in .env file")

print()
print("=" * 80)

