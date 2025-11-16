"""
Direct test of Circle API with wallet ID
Tests the wallet balance retrieval directly
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Wallet ID to test
WALLET_ID = "1fb44a6e-d042-5655-a1c0-100731f10837"

# Circle API configuration
CIRCLE_API_BASE = "https://api.circle.com"
api_key_raw = os.getenv("CIRCLE_API_KEY", "").strip()

print("=" * 80)
print("DIRECT CIRCLE API TEST")
print("=" * 80)
print(f"Wallet ID: {WALLET_ID}")
print(f"API Base URL: {CIRCLE_API_BASE}")
print()

# Normalize API key format
if not api_key_raw:
    print("[ERROR] CIRCLE_API_KEY not set in environment!")
    print("Please set CIRCLE_API_KEY in backend/.env file")
    print("Format: TEST_API_KEY:your_key_here")
    sys.exit(1)
elif api_key_raw.count(":") == 1:
    api_key = f"TEST_API_KEY:{api_key_raw}"
elif api_key_raw.count(":") == 2:
    api_key = api_key_raw
else:
    api_key = f"TEST_API_KEY:{api_key_raw}"

print(f"API Key format: {'OK' if api_key.count(':') == 2 else 'WARNING - may need format: TEST_API_KEY:key'}")

# Test 1: Get wallet balances
print()
print("[TEST 1] Getting wallet balances from Circle API...")
print(f"URL: {CIRCLE_API_BASE}/v1/w3s/developer/wallets/{WALLET_ID}/balances")
print()

try:
    url = f"{CIRCLE_API_BASE}/v1/w3s/developer/wallets/{WALLET_ID}/balances"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("Sending request...")
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("[OK] Request successful!")
        print()
        
        data = result.get("data", {})
        token_balances = data.get("tokenBalances", [])
        
        print(f"Found {len(token_balances)} token balance(s):")
        print()
        
        if len(token_balances) == 0:
            print("  No token balances found (wallet may be empty or not exist)")
        else:
            for idx, tb in enumerate(token_balances, 1):
                token = tb.get("token", {})
                amount = tb.get("amount", "0")
                symbol = token.get("symbol", "UNKNOWN")
                token_id = token.get("id", "N/A")
                token_address = token.get("address", "N/A")
                
                print(f"  [{idx}] {symbol}")
                print(f"      Amount: {amount}")
                print(f"      Token ID: {token_id}")
                print(f"      Token Address: {token_address}")
                print()
                
                # Check if USDC
                if symbol.upper() == "USDC":
                    try:
                        balance_float = float(amount)
                        print(f"  >>> USDC Balance: {balance_float} USDC <<<")
                    except ValueError:
                        print(f"  >>> USDC Balance: Could not parse amount <<<")
        
    else:
        print(f"[ERROR] Request failed!")
        print(f"Response: {response.text}")
        try:
            error_data = response.json()
            print(f"Error details: {error_data}")
        except:
            pass
            
except Exception as e:
    print(f"[ERROR] Exception occurred: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)

# Test 2: Get wallet info
print()
print("[TEST 2] Getting wallet information...")
print(f"URL: {CIRCLE_API_BASE}/v1/w3s/developer/wallets/{WALLET_ID}")
print()

try:
    url = f"{CIRCLE_API_BASE}/v1/w3s/developer/wallets/{WALLET_ID}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        wallet = result.get("data", {}).get("wallet", {})
        
        print("[OK] Wallet information:")
        print(f"  Address: {wallet.get('address', 'N/A')}")
        print(f"  State: {wallet.get('state', 'N/A')}")
        print(f"  Wallet Set ID: {wallet.get('walletSetId', 'N/A')}")
        print(f"  Wallet ID: {wallet.get('id', 'N/A')}")
    else:
        print(f"[ERROR] Request failed!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Exception occurred: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

