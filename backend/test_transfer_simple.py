"""
Simple transfer test - reloads env and attempts transfer
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Try multiple .env locations
env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent / "api.env",
]

for env_path in env_paths:
    if env_path.exists():
        print(f"Loading .env from: {env_path}")
        load_dotenv(env_path, override=True)
        break
else:
    print("Loading .env from current directory...")
    load_dotenv(override=True)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from circle_api import circle_api

# Transaction parameters
SENDER_WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
RECEIVER_ADDRESS = "0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb"
AMOUNT = "1.0"
BLOCKCHAIN = "ARC-TESTNET"

print("=" * 80)
print("USDC TRANSFER TEST")
print("=" * 80)
print(f"Sender: {SENDER_WALLET_ID}")
print(f"Receiver: {RECEIVER_ADDRESS}")
print(f"Amount: {AMOUNT} USDC")
print()

# Check credentials
entity_secret = os.getenv("ENTITY_SECRET", "").strip()
api_key = os.getenv("CIRCLE_API_KEY", "").strip()
usdc_token_id = os.getenv("USDC_TOKEN_ID", None)

print(f"ENTITY_SECRET: {'SET' if entity_secret else 'NOT SET'} ({len(entity_secret)} chars)")
print(f"CIRCLE_API_KEY: {'SET' if api_key else 'NOT SET'}")
print(f"USDC_TOKEN_ID: {usdc_token_id or 'Not set (will use default)'}")
print()

if not entity_secret:
    print("[ERROR] ENTITY_SECRET not found!")
    print("Please add ENTITY_SECRET=your_64_char_hex to backend/.env")
    sys.exit(1)

if len(entity_secret) != 64:
    print(f"[ERROR] ENTITY_SECRET must be 64 hex chars, got {len(entity_secret)}")
    sys.exit(1)

if not api_key:
    print("[ERROR] CIRCLE_API_KEY not found!")
    sys.exit(1)

# Check balance first
print("[STEP 1] Checking sender balance...")
try:
    balance = circle_api.get_wallet_balance(SENDER_WALLET_ID)
    print(f"Balance: {balance} USDC")
    if balance < float(AMOUNT):
        print(f"[WARNING] Low balance! Need {AMOUNT}, have {balance}")
except Exception as e:
    print(f"[WARNING] Could not check balance: {e}")

print()

# Execute transfer
print("[STEP 2] Executing transfer...")
print("-" * 80)

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
    print("[SUCCESS] TRANSFER INITIATED!")
    print("=" * 80)
    print(f"Transaction ID: {result.get('id')}")
    print(f"State: {result.get('state')}")
    
    tx_data = result.get('data', {})
    if tx_data.get('txHash'):
        print(f"Tx Hash: {tx_data.get('txHash')}")
    
    print()
    print("Transaction states: INITIATED → QUEUED → SENT → CONFIRMED → COMPLETE")
    
except Exception as e:
    print()
    print("=" * 80)
    print("[ERROR] TRANSFER FAILED")
    print("=" * 80)
    print(f"{e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)

