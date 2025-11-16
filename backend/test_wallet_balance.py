"""
Test script to get wallet balance using Circle API
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API key is set
api_key = os.getenv("CIRCLE_API_KEY", "").strip()
if not api_key:
    print("=" * 80)
    print("WARNING: CIRCLE_API_KEY not found in environment!")
    print("Please set CIRCLE_API_KEY in backend/.env file")
    print("=" * 80)
    print()
    print("Testing via API endpoint instead...")
    print("Make sure backend server is running on http://localhost:8000")
    print()
    
    # Try to test via API endpoint
    import requests
    
    WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
    
    # Note: This requires authentication token
    print("To test via API, use:")
    print(f"  curl -X GET 'http://localhost:8000/api/circle/wallet/balance' \\")
    print("    -H 'Authorization: Bearer YOUR_JWT_TOKEN'")
    print()
    sys.exit(1)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from circle_api import circle_api

# Wallet ID to test
WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"

print("=" * 80)
print("TESTING WALLET BALANCE")
print("=" * 80)
print(f"Wallet ID: {WALLET_ID}")
print(f"API Key: {api_key[:20]}..." if len(api_key) > 20 else f"API Key: {api_key}")
print()

# Test 1: Get wallet balance
print("[TEST 1] Getting wallet balance...")
try:
    balance = circle_api.get_wallet_balance(WALLET_ID)
    print(f"[OK] Success! Balance: {balance} USDC")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Get wallet info
print("[TEST 2] Getting wallet information...")
try:
    address = circle_api.get_wallet_address(WALLET_ID)
    print(f"[OK] Success! Address: {address}")
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Get all balances
print("[TEST 3] Getting all token balances...")
try:
    import requests
    url = f"{circle_api.base_url}/v1/w3s/developer/wallets/{WALLET_ID}/balances"
    headers = circle_api._get_headers()
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    result = response.json()
    
    token_balances = result.get("data", {}).get("tokenBalances", [])
    print(f"[OK] Success! Found {len(token_balances)} token balance(s):")
    
    for tb in token_balances:
        token = tb.get("token", {})
        print(f"  - {token.get('symbol', 'UNKNOWN')}: {tb.get('amount', '0')} (ID: {token.get('id', 'N/A')})")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

