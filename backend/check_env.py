"""
Check environment variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 80)
print("CHECKING ENVIRONMENT VARIABLES")
print("=" * 80)

# Try loading .env
env_path = Path(__file__).parent / ".env"
print(f"Looking for .env at: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path, override=True)
    print("[OK] Loaded .env file")
else:
    load_dotenv(override=True)
    print("[INFO] Using default .env loading")

print()

# Check variables
entity_secret = os.getenv("ENTITY_SECRET", "").strip()
api_key = os.getenv("CIRCLE_API_KEY", "").strip()
usdc_token_id = os.getenv("USDC_TOKEN_ID", None)

print("Variables:")
print(f"  ENTITY_SECRET: {'SET' if entity_secret else 'NOT SET'}")
if entity_secret:
    print(f"    Length: {len(entity_secret)}")
    print(f"    First 10: {entity_secret[:10]}...")
    print(f"    Last 10: ...{entity_secret[-10:]}")
    try:
        int(entity_secret, 16)
        print(f"    Valid hex: YES")
    except:
        print(f"    Valid hex: NO")
else:
    print("    [ERROR] Not found!")

print()
print(f"  CIRCLE_API_KEY: {'SET' if api_key else 'NOT SET'}")
if api_key:
    print(f"    Length: {len(api_key)}")
    print(f"    Format: {'OK' if ':' in api_key else 'May need TEST_API_KEY: prefix'}")

print()
print(f"  USDC_TOKEN_ID: {usdc_token_id or 'NOT SET'}")

print()
print("=" * 80)

if not entity_secret:
    print()
    print("TO ADD ENTITY_SECRET:")
    print("1. Open backend/.env file")
    print("2. Add line: ENTITY_SECRET=your_64_hex_characters")
    print("3. Save file")
    print("4. Run test again")

