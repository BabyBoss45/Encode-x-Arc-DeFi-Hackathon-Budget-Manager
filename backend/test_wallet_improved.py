"""
Test wallet using improved Circle API methods
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from circle_api import circle_api

# Wallet ID to test
WALLET_ID = "1fb44a6e-d042-5655-a1c0-100731f10837"

print("=" * 80)
print("TESTING WALLET WITH IMPROVED CIRCLE API")
print("=" * 80)
print(f"Wallet ID: {WALLET_ID}")
print()

# Check API key
api_key = os.getenv("CIRCLE_API_KEY", "").strip()
if not api_key:
    print("[ERROR] CIRCLE_API_KEY not set!")
    sys.exit(1)

print(f"API Key found: {api_key[:30]}...")
print()

# Test 1: Get wallet address
print("[TEST 1] Getting wallet address...")
print("-" * 80)
try:
    address = circle_api.get_wallet_address(WALLET_ID)
    if address:
        print(f"[SUCCESS] Wallet Address: {address}")
    else:
        print("[WARNING] Address not found in response")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: Get wallet balance
print("[TEST 2] Getting wallet balance...")
print("-" * 80)
try:
    balance = circle_api.get_wallet_balance(WALLET_ID)
    print(f"[SUCCESS] Balance: {balance} USDC")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Check if it's a valid UUID
print("[TEST 3] Validating UUID format...")
print("-" * 80)
is_uuid = circle_api._is_uuid(WALLET_ID)
print(f"Is valid UUID: {is_uuid}")

print()

# Test 4: Try to get public key (to verify API key works)
print("[TEST 4] Getting Circle public key (verifies API key)...")
print("-" * 80)
try:
    public_key = circle_api.get_public_key()
    if public_key:
        print(f"[SUCCESS] Public key retrieved (length: {len(public_key)} chars)")
        print("API key is valid!")
    else:
        print("[ERROR] Public key is None")
except Exception as e:
    print(f"[ERROR] Failed to get public key: {e}")
    print("This indicates API key or network issue")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

