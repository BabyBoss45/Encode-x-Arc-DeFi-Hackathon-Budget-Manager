"""
Transfer test - accepts ENTITY_SECRET from environment or command line
Usage: python test_transfer_now.py [ENTITY_SECRET]
   or: set ENTITY_SECRET=xxx && python test_transfer_now.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
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

# Get ENTITY_SECRET from command line arg or environment
entity_secret = None
if len(sys.argv) > 1:
    entity_secret = sys.argv[1].strip()
else:
    entity_secret = os.getenv("ENTITY_SECRET", "").strip()

if not entity_secret:
    print("[ERROR] ENTITY_SECRET not found!")
    print()
    print("Usage:")
    print("  python test_transfer_now.py YOUR_64_CHAR_HEX_SECRET")
    print("  or")
    print("  set ENTITY_SECRET=xxx && python test_transfer_now.py")
    sys.exit(1)

if len(entity_secret) != 64:
    print(f"[ERROR] ENTITY_SECRET must be 64 hex chars, got {len(entity_secret)}")
    sys.exit(1)

try:
    int(entity_secret, 16)
except ValueError:
    print("[ERROR] ENTITY_SECRET must be valid hex")
    sys.exit(1)

api_key = os.getenv("CIRCLE_API_KEY", "").strip()
usdc_token_id = os.getenv("USDC_TOKEN_ID", None)

print(f"[OK] ENTITY_SECRET: {entity_secret[:10]}...{entity_secret[-10:]}")
print(f"[OK] API Key: {'SET' if api_key else 'NOT SET'}")
print(f"[OK] Token ID: {usdc_token_id or 'Default'}")
print()

if not api_key:
    print("[ERROR] CIRCLE_API_KEY required!")
    sys.exit(1)

# Check balance
print("[1/3] Checking balance...")
try:
    balance = circle_api.get_wallet_balance(SENDER_WALLET_ID)
    print(f"     Balance: {balance} USDC")
    if balance < float(AMOUNT):
        print(f"     [WARNING] Low balance!")
except Exception as e:
    print(f"     [WARNING] {e}")

print()

# Execute transfer
print("[2/3] Executing transfer...")
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
    print("Status: INITIATED → QUEUED → SENT → CONFIRMED → COMPLETE")
    
except Exception as e:
    print()
    print("=" * 80)
    print("[ERROR] TRANSFER FAILED")
    print("=" * 80)
    print(f"{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 80)

