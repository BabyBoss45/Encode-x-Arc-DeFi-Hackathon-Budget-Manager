"""
Circle API client for wallet operations and payments
Uses Circle Developer-Controlled Wallets REST API with entity secret encryption
"""
import os
import uuid
import base64
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

load_dotenv()

CIRCLE_API_BASE = "https://api.circle.com"


class CircleAPI:
    def __init__(self):
        api_key_raw = os.getenv("CIRCLE_API_KEY", "").strip()
        
        # Normalize API key format
        if not api_key_raw:
            self.api_key = None
        elif api_key_raw.count(":") == 1:
            # Missing prefix, add it
            self.api_key = f"TEST_API_KEY:{api_key_raw}"
        elif api_key_raw.count(":") == 2:
            self.api_key = api_key_raw
        else:
            # No colons - assume it's just the key part, add prefix
            self.api_key = f"TEST_API_KEY:{api_key_raw}"
        
        self.base_url = CIRCLE_API_BASE
        self._public_key_cache = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key"""
        if not self.api_key:
            raise ValueError("CIRCLE_API_KEY not set in environment")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_public_key(self) -> str:
        """Get Circle's public key for encryption (cached)"""
        if self._public_key_cache:
            return self._public_key_cache
        
        url = f"{self.base_url}/v1/w3s/config/entity/publicKey"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            public_key_pem = response.json()["data"]["publicKey"]
            self._public_key_cache = public_key_pem
            return public_key_pem
        except Exception as e:
            raise RuntimeError(f"Failed to get Circle public key: {e}")
    
    def encrypt_entity_secret(self, entity_secret_hex: str) -> str:
        """
        Encrypt entity secret using RSA OAEP with SHA-256.
        
        Args:
            entity_secret_hex: Entity secret as hex string (64 characters)
            
        Returns:
            Base64-encoded encrypted ciphertext
        """
        public_key_pem = self.get_public_key()
        
        try:
            public_key = load_pem_public_key(public_key_pem.encode(), backend=default_backend())
            entity_secret_bytes = bytes.fromhex(entity_secret_hex)
            
            encrypted = public_key.encrypt(
                entity_secret_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            raise RuntimeError(f"Failed to encrypt entity secret: {e}")
    
    def transfer_usdc(
        self,
        entity_secret_hex: str,
        wallet_id: str,
        destination_address: str,
        amount: str,
        token_id: Optional[str] = None,
        token_address: Optional[str] = None,
        blockchain: str = "ARC-TESTNET"
    ) -> Dict:
        """
        Transfer USDC from Circle wallet to destination address.
        Supports both wallet ID (UUID) and wallet address as sender.
        Automatically resolves recipient wallet ID to address if needed.
        
        Args:
            entity_secret_hex: Entity secret as hex string (64 chars)
            wallet_id: Circle wallet ID (UUID) or wallet address - Company wallet (sender)
            destination_address: Recipient blockchain address or wallet ID (UUID)
            amount: Amount to transfer (as string, e.g., "10.5")
            token_id: USDC token ID (UUID) - preferred if available
            token_address: USDC token contract address - use if token_id not available
            blockchain: Blockchain identifier (default: ARC-TESTNET)
            
        Returns:
            Dict with transaction ID and state
        """
        import json
        
        print("=" * 80)
        print("[DEBUG] CircleAPI.transfer_usdc() called")
        print(f"[DEBUG] Sender: {wallet_id}")
        print(f"[DEBUG] Receiver: {destination_address}")
        print(f"[DEBUG] Amount: {amount} USDC")
        print(f"[DEBUG] Blockchain: {blockchain}")
        print(f"[DEBUG] Token ID: {token_id or 'Not provided'}")
        print(f"[DEBUG] Token Address: {token_address or 'Not provided'}")
        print("=" * 80)
        
        # Encrypt entity secret fresh for each call
        print("[DEBUG] Encrypting entity secret...")
        entity_secret_ciphertext = self.encrypt_entity_secret(entity_secret_hex)
        print("[DEBUG] Entity secret encrypted successfully")
        
        url = f"{self.base_url}/v1/w3s/developer/transactions/transfer"
        headers = self._get_headers()
        
        idempotency_key = str(uuid.uuid4())
        print(f"[DEBUG] Idempotency Key: {idempotency_key}")
        
        # Build base data
        data = {
            "idempotencyKey": idempotency_key,
            "entitySecretCiphertext": entity_secret_ciphertext,
            "amounts": [amount],
            "feeLevel": "MEDIUM"  # LOW, MEDIUM, or HIGH
        }
        
        # Handle sender: if UUID use walletId, otherwise use walletAddress + blockchain
        if self._is_uuid(wallet_id):
            data["walletId"] = wallet_id
            print(f"[DEBUG] Using sender walletId: {wallet_id}")
        else:
            # Treat as blockchain wallet address
            data["walletAddress"] = wallet_id
            data["blockchain"] = blockchain
            print(f"[DEBUG] Using sender walletAddress: {wallet_id} on {blockchain}")
        
        # Resolve recipient: if UUID, resolve to address; otherwise use as-is
        try:
            resolved_destination = self.resolve_recipient_address(destination_address)
            data["destinationAddress"] = resolved_destination
            if resolved_destination != destination_address:
                print(f"[DEBUG] Resolved recipient wallet ID to address: {resolved_destination}")
            else:
                print(f"[DEBUG] Using recipient address: {resolved_destination}")
        except Exception as e:
            raise RuntimeError(f"Failed to resolve recipient address: {e}")
        
        # Add token identifier
        if token_id:
            data["tokenId"] = token_id
            print(f"[DEBUG] Using tokenId: {token_id}")
        elif token_address:
            # Ensure blockchain is set when using tokenAddress
            if not data.get("blockchain"):
                data["blockchain"] = blockchain
            data["tokenAddress"] = token_address
            print(f"[DEBUG] Using tokenAddress: {token_address}")
        else:
            # Try to use default USDC token ID from environment
            default_token_id = os.getenv("USDC_TOKEN_ID", None)
            if default_token_id and len(default_token_id) == 36:  # Valid UUID length
                data["tokenId"] = default_token_id
                print(f"[DEBUG] Using default USDC_TOKEN_ID from env: {default_token_id}")
            else:
                # Try to find USDC token ID automatically from wallet balances
                print("[DEBUG] USDC_TOKEN_ID not set or invalid, trying to find automatically...")
                if self._is_uuid(wallet_id):
                    found_token_id = self.find_usdc_token_id(wallet_id)
                    if found_token_id:
                        data["tokenId"] = found_token_id
                        print(f"[DEBUG] Using auto-found USDC Token ID: {found_token_id}")
                    else:
                        # Fallback to default ARC-TESTNET USDC token ID
                        fallback_token_id = "15dc2b5d-0994-58b0-bf8c-3a0501148ee8"
                        data["tokenId"] = fallback_token_id
                        print(f"[DEBUG] Using fallback USDC Token ID: {fallback_token_id}")
                else:
                    raise ValueError(
                        "Either tokenId or tokenAddress must be provided, "
                        "or set USDC_TOKEN_ID in environment, "
                        "or use a valid Circle wallet ID to auto-detect"
                    )
        
        print(f"[DEBUG] Sending POST request to: {url}")
        print(f"[DEBUG] Request payload keys: {list(data.keys())}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            print(f"[DEBUG] Response status code: {response.status_code}")
            
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                # Enhanced error handling with detailed response
                error_body = None
                try:
                    error_body = response.json()
                except Exception:
                    error_body = response.text
                
                error_details = {
                    "status_code": response.status_code,
                    "response": error_body,
                    "request_payload": {k: v for k, v in data.items() if k != "entitySecretCiphertext"}
                }
                
                print(f"[DEBUG] HTTP Error details:")
                print(json.dumps(error_details, indent=2, default=str))
                
                error_msg = f"Circle API HTTP Error: {response.status_code}"
                if isinstance(error_body, dict):
                    error_msg += f" - {error_body.get('message', error_body)}"
                else:
                    error_msg += f" - {error_body}"
                
                raise RuntimeError(error_msg)
            
            result = response.json()
            
            transaction_data = result.get("data", {})
            transaction_id = transaction_data.get("id")
            state = transaction_data.get("state")
            
            print(f"[DEBUG] Transaction ID: {transaction_id}")
            print(f"[DEBUG] Transaction State: {state}")
            
            if not transaction_id:
                raise RuntimeError("No transaction ID in response")
            
            print("[DEBUG] Transfer initiated successfully")
            print("=" * 80)
            
            return {
                "id": transaction_id,
                "state": state,
                "data": transaction_data
            }
        except RuntimeError:
            # Re-raise RuntimeError as-is (already formatted)
            raise
        except Exception as e:
            print(f"[DEBUG] Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to transfer USDC: {e}")
    
    def find_usdc_token_id(self, wallet_id: str) -> Optional[str]:
        """
        Find USDC token ID from wallet balances.
        
        Args:
            wallet_id: Circle wallet ID (UUID)
            
        Returns:
            USDC token ID (UUID) or None if not found
        """
        url = f"{self.base_url}/v1/w3s/developer/wallets/{wallet_id}/balances"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            token_balances = result.get("data", {}).get("tokenBalances", [])
            
            # Find USDC token
            for tb in token_balances:
                token = tb.get("token", {})
                if token.get("symbol", "").upper() == "USDC":
                    token_id = token.get("id")
                    if token_id:
                        print(f"[DEBUG] Found USDC Token ID: {token_id}")
                        return token_id
            
            print("[DEBUG] USDC token ID not found in wallet balances")
            return None
        except Exception as e:
            print(f"[DEBUG] Warning: Failed to find USDC token ID: {e}")
            return None
    
    def get_usdc_balance(self, wallet_id: str) -> float:
        """
        Get USDC balance for a specific wallet using the wallets/balances endpoint.
        This method uses the endpoint that returns all wallets and filters by wallet_id.
        
        Args:
            wallet_id: Circle wallet ID (UUID)
            
        Returns:
            USDC balance as float (0.0 if not found or error)
        """
        print(f"[DEBUG] CircleAPI.get_usdc_balance() called for wallet_id: {wallet_id}")
        
        url = f"{self.base_url}/v1/w3s/developer/wallets/balances"
        headers = self._get_headers()
        
        # Get USDC token ID from environment or use default
        usdc_token_id = os.getenv("USDC_TOKEN_ID", "15dc2b5d-0994-58b0-bf8c-3a0501148ee8")  # Default ARC-TESTNET USDC token ID
        blockchain = os.getenv("BLOCKCHAIN", "ARC-TESTNET")
        
        # If USDC_TOKEN_ID not set, use the default from test
        if not usdc_token_id or len(usdc_token_id) != 36:
            usdc_token_id = "15dc2b5d-0994-58b0-bf8c-3a0501148ee8"
            print(f"[DEBUG] Using default USDC_TOKEN_ID: {usdc_token_id}")
        
        params = {
            "blockchain": blockchain,
            "pageSize": 50,
        }
        
        try:
            print(f"[DEBUG] Request URL: {url}")
            print(f"[DEBUG] Request params: {params}")
            print(f"[DEBUG] Looking for wallet_id: {wallet_id}")
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"[DEBUG] Response status: {response.status_code}")
            
            response.raise_for_status()
            
            response_json = response.json()
            print(f"[DEBUG] Response JSON keys: {list(response_json.keys())}")
            
            data = response_json.get("data", {})
            print(f"[DEBUG] Data keys: {list(data.keys())}")
            
            wallets = data.get("wallets", [])
            
            print(f"[DEBUG] Found {len(wallets)} wallet(s) in response")
            
            # Log all wallet IDs for debugging
            if wallets:
                print(f"[DEBUG] Wallet IDs in response:")
                for idx, w in enumerate(wallets):
                    w_id = w.get("id", "N/A")
                    print(f"[DEBUG]   {idx + 1}. {w_id}")
            
            # Find the specific wallet
            found_wallet = False
            for w in wallets:
                w_id = w.get("id")
                if w_id != wallet_id:
                    continue
                
                found_wallet = True
                print(f"[DEBUG] ✓ Found matching wallet: {wallet_id}")
                token_balances = w.get("tokenBalances", [])
                print(f"[DEBUG] Found {len(token_balances)} token balance(s)")
                
                # Log all tokens for debugging
                if token_balances:
                    print(f"[DEBUG] Tokens in wallet:")
                    for idx, tb in enumerate(token_balances):
                        token = tb.get("token", {})
                        token_symbol = token.get("symbol", "N/A")
                        token_id = token.get("id", "N/A")
                        amount = tb.get("amount", "0")
                        print(f"[DEBUG]   {idx + 1}. {token_symbol} (ID: {token_id}) - Amount: {amount}")
                
                # Find USDC token balance
                for tb in token_balances:
                    token = tb.get("token", {})
                    
                    # Check by token ID if available
                    if usdc_token_id and token.get("id") == usdc_token_id:
                        amount_str = tb.get("amount", "0")
                        try:
                            balance = float(amount_str)
                            print(f"[DEBUG] ✓ Found USDC balance by token_id: {balance} USDC")
                            return balance
                        except ValueError:
                            print(f"[DEBUG] ✗ Invalid amount format: {amount_str}")
                            return 0.0
                    
                    # Check by symbol if token ID not specified or doesn't match
                    if token.get("symbol", "").upper() == "USDC":
                        amount_str = tb.get("amount", "0")
                        try:
                            balance = float(amount_str)
                            print(f"[DEBUG] ✓ Found USDC balance by symbol: {balance} USDC")
                            return balance
                        except ValueError:
                            print(f"[DEBUG] ✗ Invalid amount format: {amount_str}")
                            return 0.0
                
                print(f"[DEBUG] ✗ USDC token not found in wallet balances")
                return 0.0
            
            if not found_wallet:
                print(f"[DEBUG] ✗ Wallet {wallet_id} not found in response")
                print(f"[DEBUG] Available wallet IDs: {[w.get('id') for w in wallets]}")
            return 0.0
            
        except requests.exceptions.RequestException as e:
            print(f"[BALANCE ERROR] Request failed: {e}")
            return 0.0
        except Exception as e:
            print(f"[BALANCE ERROR] {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def get_wallet_balance(self, wallet_id: str, token_id: Optional[str] = None) -> float:
        """
        Get USDC balance for a Circle wallet.
        
        Args:
            wallet_id: Circle wallet ID (UUID) - Company wallet ID
            token_id: USDC token ID (UUID) - if None, will try to find USDC
            
        Returns:
            USDC balance as float (0.0 if not found or error)
        """
        print(f"[DEBUG] CircleAPI.get_wallet_balance() called")
        print(f"[DEBUG] Wallet ID: {wallet_id}")
        print(f"[DEBUG] Token ID: {token_id or 'Not provided (will search by symbol)'}")
        
        url = f"{self.base_url}/v1/w3s/developer/wallets/{wallet_id}/balances"
        headers = self._get_headers()
        
        try:
            print(f"[DEBUG] Sending GET request to: {url}")
            response = requests.get(url, headers=headers)
            print(f"[DEBUG] Response status code: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            
            token_balances = result.get("data", {}).get("tokenBalances", [])
            print(f"[DEBUG] Found {len(token_balances)} token balance(s)")
            
            # Find USDC token balance
            for tb in token_balances:
                token = tb.get("token", {})
                token_symbol = token.get("symbol", "N/A")
                token_id_found = token.get("id", "N/A")
                print(f"[DEBUG] Checking token: {token_symbol} (ID: {token_id_found})")
                
                # Check by token_id if provided
                if token_id and token.get("id") == token_id:
                    amount_str = tb.get("amount", "0")
                    try:
                        balance = float(amount_str)
                        print(f"[DEBUG] Found USDC balance by token_id: {balance} USDC")
                        return balance
                    except ValueError:
                        print(f"[DEBUG] Invalid amount format: {amount_str}")
                        return 0.0
                
                # Check by symbol if token_id not provided
                if not token_id and token.get("symbol", "").upper() == "USDC":
                    amount_str = tb.get("amount", "0")
                    try:
                        balance = float(amount_str)
                        print(f"[DEBUG] Found USDC balance by symbol: {balance} USDC")
                        return balance
                    except ValueError:
                        print(f"[DEBUG] Invalid amount format: {amount_str}")
                        return 0.0
            
            print("[DEBUG] USDC token not found in balances")
            return 0.0
        except Exception as e:
            # Return 0.0 on error (don't fail dashboard if balance check fails)
            print(f"[DEBUG] Warning: Failed to get wallet balance: {e}")
            return 0.0
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict]:
        """
        Get transaction status from Circle API.
        
        Args:
            transaction_id: Circle transaction ID (UUID)
            
        Returns:
            Dict with transaction data or None if error
        """
        url = f"{self.base_url}/v1/w3s/developer/transactions/{transaction_id}"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            transaction = result.get("data", {}).get("transaction", {})
            return {
                "id": transaction.get("id"),
                "state": transaction.get("state"),
                "txHash": transaction.get("txHash"),
                "data": transaction
            }
        except Exception as e:
            print(f"Warning: Failed to get transaction status: {e}")
            return None
    
    def get_wallet_transactions(self, wallet_id: str, limit: int = 50) -> list:
        """
        Get all transactions for a wallet from Circle API.
        
        Args:
            wallet_id: Circle wallet ID (UUID)
            limit: Maximum number of transactions to return (default: 50)
            
        Returns:
            List of transaction dictionaries or empty list if error
        """
        url = f"{self.base_url}/v1/w3s/developer/transactions"
        headers = self._get_headers()
        
        params = {
            "walletIds": wallet_id,
            "pageSize": limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract transactions from response
            transactions = result.get("data", {}).get("transactions", [])
            return transactions if transactions else []
        except Exception as e:
            print(f"Warning: Failed to get wallet transactions: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_wallet_address(self, wallet_id: str) -> Optional[str]:
        """
        Get blockchain address for a Circle wallet ID.
        Handles different response formats from Circle API.
        
        Args:
            wallet_id: Circle wallet ID (UUID)
            
        Returns:
            Blockchain address or None if error
        """
        url = f"{self.base_url}/v1/w3s/developer/wallets/{wallet_id}"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            data = result.get("data", {})
            
            # Try different response formats
            wallet = data.get("wallet") or data.get("wallets")
            
            # Handle wallet as dict
            if isinstance(wallet, dict):
                address = wallet.get("address")
                if address:
                    return address
            
            # Handle wallet as list
            if isinstance(wallet, list) and len(wallet) > 0:
                address = wallet[0].get("address")
                if address:
                    return address
            
            # Fallback: check top-level data fields
            if "address" in data:
                return data.get("address")
            
            return None
        except Exception as e:
            print(f"Warning: Failed to get wallet address: {e}")
            return None
    
    def _is_uuid(self, value: str) -> bool:
        """
        Check if a string is a valid UUID format.
        
        Args:
            value: String to check
            
        Returns:
            True if value is a valid UUID format
        """
        import re
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.I
        )
        return bool(uuid_pattern.match(value))
    
    def resolve_recipient_address(self, recipient: str) -> str:
        """
        Resolve recipient to on-chain address.
        If recipient is a wallet ID (UUID), resolves it to address.
        Otherwise returns recipient as-is (assuming it's already an address).
        
        Args:
            recipient: Wallet ID (UUID) or blockchain address
            
        Returns:
            Blockchain address
        """
        if self._is_uuid(recipient):
            # Resolve wallet ID to address
            address = self.get_wallet_address(recipient)
            if not address:
                raise RuntimeError(
                    f"Could not resolve wallet ID {recipient} to an on-chain address"
                )
            return address
        else:
            # Assume it's already an address
            return recipient


# Global instance
circle_api = CircleAPI()
