"""
Test USDC transfer using Circle API
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
print("TESTING USDC TRANSFER")
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

if not entity_secret:
    print("[ERROR] ENTITY_SECRET not set in .env file!")
    print("Please set ENTITY_SECRET in backend/.env")
    print()
    print("ENTITY_SECRET is a 64-character hex string used to sign transactions.")
    print("You can find it in your Circle Dashboard under Developer Settings.")
    print()
    print("Example .env entry:")
    print("  ENTITY_SECRET=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    sys.exit(1)

if not api_key:
    print("[ERROR] CIRCLE_API_KEY not set in .env file!")
    print("Please set CIRCLE_API_KEY in backend/.env")
    sys.exit(1)

if len(entity_secret) != 64:
    print(f"[ERROR] ENTITY_SECRET must be 64 hex characters, got {len(entity_secret)}")
    sys.exit(1)

print(f"[INFO] Entity Secret: {entity_secret[:10]}...{entity_secret[-10:]}")
print(f"[INFO] API Key: {api_key[:30]}...")
if usdc_token_id:
    print(f"[INFO] USDC Token ID: {usdc_token_id}")
else:
    print("[INFO] USDC Token ID: Not set (will try to find by symbol)")
print()

# Step 1: Check sender wallet balance
print("[STEP 1] Checking sender wallet balance...")
print("-" * 80)
try:
    balance = circle_api.get_wallet_balance(SENDER_WALLET_ID)
    print(f"[OK] Sender balance: {balance} USDC")
    
    amount_float = float(AMOUNT)
    if balance < amount_float:
        print(f"[WARNING] Insufficient balance! Need {amount_float} USDC, have {balance} USDC")
        print("Transaction may fail!")
    else:
        print(f"[OK] Sufficient balance for transfer")
except Exception as e:
    print(f"[WARNING] Could not check balance: {e}")
    print("Continuing with transfer attempt...")

print()

# Step 2: Get sender wallet address (for verification)
print("[STEP 2] Getting sender wallet address...")
print("-" * 80)
try:
    sender_address = circle_api.get_wallet_address(SENDER_WALLET_ID)
    if sender_address:
        print(f"[OK] Sender address: {sender_address}")
    else:
        print("[WARNING] Could not get sender address")
except Exception as e:
    print(f"[WARNING] Could not get sender address: {e}")

print()

# Step 3: Execute transfer
print("[STEP 3] Executing transfer...")
print("-" * 80)
print("This will create a transaction on Circle API")
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
    print("Transaction states:")
    print("  INITIATED - Transaction created")
    print("  QUEUED - Transaction in queue")
    print("  SENT - Transaction sent to blockchain")
    print("  CONFIRMED - Transaction confirmed")
    print("  COMPLETE - Transaction completed")
    print()
    print("You can check transaction status using:")
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

