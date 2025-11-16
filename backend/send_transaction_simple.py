"""
Simple transaction script - accepts ENTITY_SECRET as command line argument
Usage: python send_transaction_simple.py YOUR_ENTITY_SECRET
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).parent / ".env")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from circle_api import circle_api

# Transaction parameters
SENDER_WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
RECEIVER_ADDRESS = "0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb"
AMOUNT = "1.0"
BLOCKCHAIN = "ARC-TESTNET"

print("=" * 80)
print("SENDING 1 USDC TRANSACTION")
print("=" * 80)
print(f"From: {SENDER_WALLET_ID}")
print(f"To:   {RECEIVER_ADDRESS}")
print()

# Get ENTITY_SECRET from command line or env
if len(sys.argv) > 1:
    entity_secret = sys.argv[1].strip()
    print(f"[OK] Using ENTITY_SECRET from command line")
else:
    entity_secret = os.getenv("ENTITY_SECRET", "").strip()
    if entity_secret:
        print(f"[OK] Using ENTITY_SECRET from .env")
    else:
        print("[ERROR] ENTITY_SECRET required!")
        print()
        print("Usage: python send_transaction_simple.py YOUR_64_CHAR_HEX_SECRET")
        sys.exit(1)

if len(entity_secret) != 64:
    print(f"[ERROR] ENTITY_SECRET must be 64 hex chars, got {len(entity_secret)}")
    sys.exit(1)

api_key = os.getenv("CIRCLE_API_KEY", "").strip()
if not api_key:
    print("[ERROR] CIRCLE_API_KEY not found")
    sys.exit(1)

print()

# Check balance
print("Checking balance...")
try:
    balance = circle_api.get_wallet_balance(SENDER_WALLET_ID)
    print(f"Balance: {balance} USDC")
except Exception as e:
    print(f"[WARNING] {e}")

print()

# Send transaction
print("Sending transaction...")

# Try to get USDC token ID from balances first
usdc_token_id = None
try:
    import requests
    url = f"{circle_api.base_url}/v1/w3s/developer/wallets/{SENDER_WALLET_ID}/balances"
    headers = circle_api._get_headers()
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        result = response.json()
        token_balances = result.get("data", {}).get("tokenBalances", [])
        for tb in token_balances:
            token = tb.get("token", {})
            if token.get("symbol", "").upper() == "USDC":
                usdc_token_id = token.get("id")
                print(f"[INFO] Found USDC Token ID: {usdc_token_id}")
                break
except Exception as e:
    print(f"[INFO] Could not get token ID automatically: {e}")

# Use correct token ID from example code
if not usdc_token_id:
    usdc_token_id = "15dc2b5d-0994-58b0-bf8c-3a0501148ee8"  # Full UUID from example
    print(f"[INFO] Using default USDC Token ID: {usdc_token_id}")

try:
    result = circle_api.transfer_usdc(
        entity_secret_hex=entity_secret,
        wallet_id=SENDER_WALLET_ID,
        destination_address=RECEIVER_ADDRESS,
        amount=AMOUNT,
        token_id=usdc_token_id,
        blockchain=BLOCKCHAIN
    )
    
    print()
    print("=" * 80)
    print("[SUCCESS] TRANSACTION SENT!")
    print("=" * 80)
    print(f"Transaction ID: {result.get('id')}")
    print(f"State: {result.get('state')}")
    
    if result.get('data', {}).get('txHash'):
        print(f"Tx Hash: {result.get('data', {}).get('txHash')}")
    
except Exception as e:
    print()
    print("=" * 80)
    print("[ERROR] FAILED")
    print("=" * 80)
    print(f"{e}")
    sys.exit(1)

print()
print("=" * 80)

