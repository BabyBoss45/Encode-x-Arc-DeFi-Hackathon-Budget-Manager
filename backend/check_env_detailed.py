"""
Detailed check of .env file loading
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"

print("=" * 80)
print("DETAILED .ENV CHECK")
print("=" * 80)
print(f"File path: {env_path}")
print(f"File exists: {env_path.exists()}")
print()

if env_path.exists():
    # Try to read raw file (first 20 lines)
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"Total lines in file: {len(lines)}")
            print()
            print("First 20 lines:")
            for i, line in enumerate(lines[:20], 1):
                # Don't show full secrets, just first/last chars
                if 'ENTITY_SECRET' in line or 'SECRET' in line.upper():
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if len(value) > 10:
                            masked = value[:5] + "..." + value[-5:]
                        else:
                            masked = "***"
                        print(f"  {i}: {key}={masked} (length: {len(value)})")
                    else:
                        print(f"  {i}: {line.rstrip()}")
                else:
                    print(f"  {i}: {line.rstrip()}")
    except Exception as e:
        print(f"Error reading file: {e}")

print()
print("-" * 80)
print("Loading .env...")
load_dotenv(env_path, override=True)

print()
print("Environment variables after loading:")
entity_secret = os.getenv("ENTITY_SECRET", "").strip()
api_key = os.getenv("CIRCLE_API_KEY", "").strip()

print(f"ENTITY_SECRET:")
print(f"  Found: {'YES' if entity_secret else 'NO'}")
if entity_secret:
    print(f"  Length: {len(entity_secret)}")
    print(f"  First 5: {entity_secret[:5]}")
    print(f"  Last 5: {entity_secret[-5:]}")
    try:
        int(entity_secret, 16)
        print(f"  Valid hex: YES")
    except:
        print(f"  Valid hex: NO")
else:
    print("  Value: (empty)")

print()
print(f"CIRCLE_API_KEY:")
print(f"  Found: {'YES' if api_key else 'NO'}")
if api_key:
    print(f"  Length: {len(api_key)}")
    print(f"  First 20: {api_key[:20]}...")

print()
print("=" * 80)

