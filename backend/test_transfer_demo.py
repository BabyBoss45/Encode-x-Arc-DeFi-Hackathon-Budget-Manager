"""
Demo test transfer - shows what's needed and attempts transfer if credentials are available
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from circle_api import circle_api

# Transaction parameters
SENDER_WALLET_ID = "a35494a6-3d52-5eeb-8b42-b3bb5ec9a4d7"
RECEIVER_ADDRESS = "0x7cec508e78d5d18ea5c14d846a05bab3a017d5eb"
AMOUNT = "1.0"  # 1 USDC
BLOCKCHAIN = "ARC-TESTNET"

print("=" * 80)
print("USDC TRANSFER TEST")
print("=" * 80)
print(f"Sender Wallet ID: {SENDER_WALLET_ID}")
print(f"Receiver Address: {RECEIVER_ADDRESS}")
print(f"Amount: {AMOUNT} USDC")
print(f"Blockchain: {BLOCKCHAIN}")
print()

# Check environment variables
entity_secret = os.getenv("ENTITY_SECRET", "").strip()
api_key = os.getenv("CIRCLE_API_KEY", "").strip()
usdc_token_id = os.getenv("USDC_TOKEN_ID", None)

print("[CHECK] Environment variables:")
print(f"  CIRCLE_API_KEY: {'SET' if api_key else 'NOT SET'}")
print(f"  ENTITY_SECRET: {'SET' if entity_secret else 'NOT SET'} ({len(entity_secret)} chars)")
print(f"  USDC_TOKEN_ID: {'SET' if usdc_token_id else 'NOT SET (optional)'}")
print()

if not entity_secret:
    print("[ERROR] ENTITY_SECRET is required for transfers!")
    print()
    print("To perform a transfer, you need:")
    print("1. Set ENTITY_SECRET in backend/.env (64 hex characters)")
    print("2. Set CIRCLE_API_KEY in backend/.env")
    print("3. Optionally set USDC_TOKEN_ID in backend/.env")
    print()
    print("Example .env content:")
    print("  CIRCLE_API_KEY=TEST_API_KEY:your_key_here")
    print("  ENTITY_SECRET=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    print("  USDC_TOKEN_ID=15dc2b5d-0994-58b0-bf8c-3a0501148ee8")
    print()
    print("Without ENTITY_SECRET, I can only show you the transfer code structure.")
    sys.exit(0)

if len(entity_secret) != 64:
    print(f"[ERROR] ENTITY_SECRET must be 64 hex characters, got {len(entity_secret)}")
    sys.exit(1)

if not api_key:
    print("[ERROR] CIRCLE_API_KEY is required!")
    sys.exit(1)

# All checks passed, proceed with transfer
print("[OK] All required credentials are set")
print()

# Step 1: Check sender wallet balance
print("[STEP 1] Checking sender wallet balance...")
print("-" * 80)
try:
    balance = circle_api.get_wallet_balance(SENDER_WALLET_ID)
    print(f"Balance: {balance} USDC")
    
    amount_float = float(AMOUNT)
    if balance < amount_float:
        print(f"[WARNING] Insufficient balance! Need {amount_float} USDC, have {balance} USDC")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Transfer cancelled")
            sys.exit(0)
    else:
        print(f"[OK] Sufficient balance ✓")
except Exception as e:
    print(f"[WARNING] Could not check balance: {e}")
    print("Continuing with transfer attempt...")

print()

# Step 2: Get sender wallet address
print("[STEP 2] Getting sender wallet address...")
print("-" * 80)
try:
    sender_address = circle_api.get_wallet_address(SENDER_WALLET_ID)
    if sender_address:
        print(f"Address: {sender_address}")
    else:
        print("[WARNING] Could not get sender address")
except Exception as e:
    print(f"[WARNING] Could not get sender address: {e}")

print()

# Step 3: Execute transfer
print("[STEP 3] Executing transfer...")
print("-" * 80)
print("Creating transaction on Circle API...")
print()

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
    print(f"Transaction State: {result.get('state')}")
    
    tx_data = result.get('data', {})
    if tx_data.get('txHash'):
        print(f"Transaction Hash: {tx_data.get('txHash')}")
    
    print()
    print("Transaction is being processed. States:")
    print("  INITIATED → QUEUED → SENT → CONFIRMED → COMPLETE")
    print()
    print("Check status:")
    print(f"  GET /api/circle/transaction/{result.get('id')}")
    
except Exception as e:
    print()
    print("=" * 80)
    print("[ERROR] TRANSFER FAILED")
    print("=" * 80)
    print(f"Error: {e}")
    print()
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

