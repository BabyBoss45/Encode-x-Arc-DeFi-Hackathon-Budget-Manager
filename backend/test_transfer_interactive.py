"""
Interactive transfer test - prompts for ENTITY_SECRET if not found
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
print(f"Sender Wallet ID: {SENDER_WALLET_ID}")
print(f"Receiver Address: {RECEIVER_ADDRESS}")
print(f"Amount: {AMOUNT} USDC")
print(f"Blockchain: {BLOCKCHAIN}")
print()

# Get ENTITY_SECRET
entity_secret = os.getenv("ENTITY_SECRET", "").strip()

if not entity_secret:
    print("[INFO] ENTITY_SECRET not found in .env file")
    print("Please enter your ENTITY_SECRET (64 hex characters):")
    entity_secret = input("ENTITY_SECRET: ").strip()

if not entity_secret:
    print("[ERROR] ENTITY_SECRET is required!")
    sys.exit(1)

if len(entity_secret) != 64:
    print(f"[ERROR] ENTITY_SECRET must be exactly 64 hex characters, got {len(entity_secret)}")
    sys.exit(1)

# Validate hex
try:
    int(entity_secret, 16)
except ValueError:
    print("[ERROR] ENTITY_SECRET must be a valid hex string")
    sys.exit(1)

# Get other config
api_key = os.getenv("CIRCLE_API_KEY", "").strip()
usdc_token_id = os.getenv("USDC_TOKEN_ID", None)

print()
print(f"[OK] ENTITY_SECRET: {entity_secret[:10]}...{entity_secret[-10:]}")
print(f"[OK] CIRCLE_API_KEY: {'SET' if api_key else 'NOT SET'}")
print(f"[OK] USDC_TOKEN_ID: {usdc_token_id or 'Not set (will use default)'}")
print()

if not api_key:
    print("[ERROR] CIRCLE_API_KEY is required!")
    sys.exit(1)

# Step 1: Check balance
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

# Step 2: Get sender address
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
    print("Transaction is being processed.")
    print("States: INITIATED → QUEUED → SENT → CONFIRMED → COMPLETE")
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

