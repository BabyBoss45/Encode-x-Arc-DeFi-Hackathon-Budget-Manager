#!/usr/bin/env python3
"""
Test script to check USDC balance retrieval using Circle API
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CIRCLE_API_BASE = "https://api.circle.com"
API_KEY = os.getenv("CIRCLE_API_KEY", "").strip()
SOURCE_WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
USDC_TOKEN_ID = "15dc2b5d-0994-58b0-bf8c-3a0501148ee8"
BLOCKCHAIN = "ARC-TESTNET"

def get_usdc_balance():
    """
    Get USDC balance for SOURCE_WALLET_ID using the wallets/balances endpoint
    """
    url = f"{CIRCLE_API_BASE}/v1/w3s/developer/wallets/balances"
    
    # Normalize API key format
    if not API_KEY:
        print("[ERROR] CIRCLE_API_KEY not set in environment!")
        return None
    
    if API_KEY.count(":") == 1:
        # Missing prefix, add it
        api_key_formatted = f"TEST_API_KEY:{API_KEY}"
    elif API_KEY.count(":") == 2:
        api_key_formatted = API_KEY
    else:
        # No colons - assume it's just the key part, add prefix
        api_key_formatted = f"TEST_API_KEY:{API_KEY}"
    
    headers = {
        "Authorization": f"Bearer {api_key_formatted}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    params = {
        "blockchain": BLOCKCHAIN,
        "pageSize": 50,
    }
    
    print("=" * 80)
    print("TESTING USDC BALANCE RETRIEVAL")
    print("=" * 80)
    print(f"API Base: {CIRCLE_API_BASE}")
    print(f"Wallet ID: {SOURCE_WALLET_ID}")
    print(f"USDC Token ID: {USDC_TOKEN_ID}")
    print(f"Blockchain: {BLOCKCHAIN}")
    print(f"API Key (first 20 chars): {api_key_formatted[:20]}...")
    print()
    
    try:
        print(f"[1] Sending GET request to: {url}")
        print(f"[1] Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"[2] Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[ERROR] Request failed with status {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return None
        
        response.raise_for_status()
        
        data = response.json().get("data", {})
        wallets = data.get("wallets", [])
        
        print(f"[3] Found {len(wallets)} wallet(s) in response")
        print()
        
        # Log all wallet IDs for debugging
        if wallets:
            print("[4] Wallet IDs in response:")
            for idx, w in enumerate(wallets, 1):
                w_id = w.get("id", "N/A")
                print(f"    {idx}. {w_id}")
            print()
        
        # Find the specific wallet
        found_wallet = False
        for w in wallets:
            w_id = w.get("id")
            if w_id != SOURCE_WALLET_ID:
                continue
            
            found_wallet = True
            print(f"[5] [OK] Found matching wallet: {SOURCE_WALLET_ID}")
            
            token_balances = w.get("tokenBalances", [])
            print(f"[6] Found {len(token_balances)} token balance(s)")
            print()
            
            # Log all tokens for debugging
            if token_balances:
                print("[7] Tokens in wallet:")
                for idx, tb in enumerate(token_balances, 1):
                    token = tb.get("token", {})
                    token_symbol = token.get("symbol", "N/A")
                    token_id = token.get("id", "N/A")
                    amount = tb.get("amount", "0")
                    print(f"    {idx}. {token_symbol} (ID: {token_id}) - Amount: {amount}")
                print()
            
            # Find USDC token balance
            for tb in token_balances:
                token = tb.get("token", {})
                
                # Check by token ID if available
                if USDC_TOKEN_ID and token.get("id") == USDC_TOKEN_ID:
                    amount_str = tb.get("amount", "0")
                    try:
                        balance = float(amount_str)
                        print(f"[8] [OK] Found USDC balance by token_id: {balance} USDC")
                        print("=" * 80)
                        print(f"RESULT: {balance} USDC")
                        print("=" * 80)
                        return balance
                    except ValueError:
                        print(f"[ERROR] Invalid amount format: {amount_str}")
                        return None
                
                # Check by symbol if token ID not specified or doesn't match
                if token.get("symbol", "").upper() == "USDC":
                    amount_str = tb.get("amount", "0")
                    try:
                        balance = float(amount_str)
                        print(f"[8] [OK] Found USDC balance by symbol: {balance} USDC")
                        print("=" * 80)
                        print(f"RESULT: {balance} USDC")
                        print("=" * 80)
                        return balance
                    except ValueError:
                        print(f"[ERROR] Invalid amount format: {amount_str}")
                        return None
            
            print("[8] [WARNING] USDC token not found in wallet balances")
            print("=" * 80)
            print("RESULT: 0.0 USDC (USDC token not found)")
            print("=" * 80)
            return 0.0
        
        if not found_wallet:
            print(f"[5] [ERROR] Wallet {SOURCE_WALLET_ID} not found in response")
            print(f"[5] Available wallet IDs: {[w.get('id') for w in wallets]}")
            print("=" * 80)
            print("RESULT: Wallet not found")
            print("=" * 80)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    balance = get_usdc_balance()
    if balance is not None:
        print(f"\n[SUCCESS] Test completed successfully!")
        print(f"Balance: {balance} USDC")
    else:
        print(f"\n[FAILED] Test failed - check errors above")

