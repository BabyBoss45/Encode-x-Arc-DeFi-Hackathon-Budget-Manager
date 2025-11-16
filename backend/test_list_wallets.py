"""
Test to list all wallets in Circle account
This helps verify API key and find correct wallet IDs
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CIRCLE_API_BASE = "https://api.circle.com"
api_key_raw = os.getenv("CIRCLE_API_KEY", "").strip()

print("=" * 80)
print("LISTING ALL WALLETS IN CIRCLE ACCOUNT")
print("=" * 80)
print()

# Normalize API key
if not api_key_raw:
    print("[ERROR] CIRCLE_API_KEY not set!")
    exit(1)

if api_key_raw.count(":") == 1:
    api_key = f"TEST_API_KEY:{api_key_raw}"
elif api_key_raw.count(":") == 2:
    api_key = api_key_raw
else:
    api_key = f"TEST_API_KEY:{api_key_raw}"

print(f"API Key: {api_key[:30]}...")
print()

# Try to list wallets
print("[TEST] Getting list of wallets...")
print(f"URL: {CIRCLE_API_BASE}/v1/w3s/developer/wallets")
print()

try:
    url = f"{CIRCLE_API_BASE}/v1/w3s/developer/wallets"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Try with pagination
    params = {
        "pageSize": 100
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("[SUCCESS] Request successful!")
        print()
        
        data = result.get("data", {})
        wallets = data.get("wallets", [])
        
        print(f"Found {len(wallets)} wallet(s):")
        print()
        
        if len(wallets) == 0:
            print("  No wallets found in this account")
            print("  You may need to create a wallet first")
        else:
            target_wallet_id = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
            found_target = False
            
            for idx, wallet in enumerate(wallets, 1):
                wallet_id = wallet.get("id", "N/A")
                address = wallet.get("address", "N/A")
                state = wallet.get("state", "N/A")
                wallet_set_id = wallet.get("walletSetId", "N/A")
                
                is_target = wallet_id == target_wallet_id
                if is_target:
                    found_target = True
                    print(f"  >>> [{idx}] TARGET WALLET FOUND! <<<")
                else:
                    print(f"  [{idx}]")
                
                print(f"      Wallet ID: {wallet_id}")
                print(f"      Address: {address}")
                print(f"      State: {state}")
                print(f"      Wallet Set ID: {wallet_set_id}")
                print()
            
            if not found_target:
                print()
                print(f"[WARNING] Target wallet ID '{target_wallet_id}' not found in list!")
                print("Please check the wallet ID or use one from the list above")
        
        # Also show pagination info
        pagination = data.get("pagination", {})
        if pagination:
            print(f"Pagination: {pagination}")
        
    elif response.status_code == 401:
        print("[ERROR] Unauthorized - Invalid API key")
        print("Please check your CIRCLE_API_KEY in .env file")
    elif response.status_code == 404:
        print("[ERROR] Endpoint not found")
        print("This might be a testnet vs mainnet issue")
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
print("TEST COMPLETE")
print("=" * 80)

