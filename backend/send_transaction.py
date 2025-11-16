"""
Simple script to send USDC transaction via Circle API
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from multiple possible locations
env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        print(f"[INFO] Loaded .env from: {env_path}")
        break
else:
    # Try default location
    load_dotenv(override=True)
    print("[INFO] Using default .env loading")

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from circle_api import circle_api

# Transaction parameters
SENDER_WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
RECEIVER_ADDRESS = "0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb"
AMOUNT = "1.0"  # 1 USDC
BLOCKCHAIN = "ARC-TESTNET"

print("=" * 80)
print("SENDING USDC TRANSACTION")
print("=" * 80)
print(f"From: {SENDER_WALLET_ID}")
print(f"To:   {RECEIVER_ADDRESS}")
print(f"Amount: {AMOUNT} USDC")
print()

# Get credentials (allow command line override)
entity_secret = None
if len(sys.argv) > 1:
    entity_secret = sys.argv[1].strip()
    print(f"[INFO] Using ENTITY_SECRET from command line")
else:
    entity_secret = os.getenv("ENTITY_SECRET", "").strip()

api_key = os.getenv("CIRCLE_API_KEY", "").strip()

# Debug: show what we found
print(f"[DEBUG] ENTITY_SECRET: {'SET' if entity_secret else 'NOT SET'} ({len(entity_secret) if entity_secret else 0} chars)")
print(f"[DEBUG] CIRCLE_API_KEY: {'SET' if api_key else 'NOT SET'}")

if not entity_secret:
    print()
    print("[ERROR] ENTITY_SECRET not found!")
    print()
    print("Options:")
    print("  1. Add ENTITY_SECRET=xxx to backend/.env file")
    print("  2. Pass as argument: python send_transaction.py YOUR_ENTITY_SECRET")
    sys.exit(1)

if not api_key:
    print("[ERROR] CIRCLE_API_KEY not found in .env")
    sys.exit(1)

if len(entity_secret) != 64:
    print(f"[ERROR] ENTITY_SECRET must be 64 hex chars, got {len(entity_secret)}")
    sys.exit(1)

print("[OK] Credentials loaded")
print()

# Check balance
print("Checking sender balance...")
try:
    balance = circle_api.get_wallet_balance(SENDER_WALLET_ID)
    print(f"Balance: {balance} USDC")
    if balance < float(AMOUNT):
        print(f"[WARNING] Low balance! Need {AMOUNT}, have {balance}")
except Exception as e:
    print(f"[WARNING] Could not check balance: {e}")

print()

# Send transaction
print("Sending transaction...")
print("-" * 80)

try:
    result = circle_api.transfer_usdc(
        entity_secret_hex=entity_secret,
        wallet_id=SENDER_WALLET_ID,
        destination_address=RECEIVER_ADDRESS,
        amount=AMOUNT,
        blockchain=BLOCKCHAIN
    )
    
    print()
    print("=" * 80)
    print("[SUCCESS] TRANSACTION SENT!")
    print("=" * 80)
    print(f"Transaction ID: {result.get('id')}")
    print(f"State: {result.get('state')}")
    
    tx_data = result.get('data', {})
    if tx_data.get('txHash'):
        print(f"Tx Hash: {tx_data.get('txHash')}")
    
    print()
    print("Transaction is being processed.")
    print("Check status: GET /api/circle/transaction/" + result.get('id'))
    
except Exception as e:
    print()
    print("=" * 80)
    print("[ERROR] TRANSACTION FAILED")
    print("=" * 80)
    print(f"{e}")
    sys.exit(1)

print()
print("=" * 80)

