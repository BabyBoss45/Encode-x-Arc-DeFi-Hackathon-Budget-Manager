"""
Circle API client for wallet operations and payments
"""
import requests
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

CIRCLE_API_KEY = os.getenv("CIRCLE_API_KEY")
CIRCLE_BASE_URL = os.getenv("CIRCLE_BASE_URL", "https://api.circle.com/v1")


class CircleAPI:
    def __init__(self):
        self.api_key = CIRCLE_API_KEY
        self.base_url = CIRCLE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_wallet(self, user_id: str) -> Dict:
        """Create a new wallet for a user"""
        url = f"{self.base_url}/w3s/developer/wallets"
        payload = {
            "idempotencyKey": f"wallet-{user_id}",
            "blockchains": ["ETH-SEPOLIA"]  # Adjust based on your needs
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_wallet_balance(self, wallet_id: str) -> Dict:
        """Get wallet balance"""
        url = f"{self.base_url}/w3s/wallets/{wallet_id}/balances"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def transfer(self, source_wallet_id: str, destination_address: str, amount: str, token_id: str = "USDC") -> Dict:
        """
        Transfer tokens from source wallet to destination address
        amount: string representation of amount (e.g., "10.5")
        token_id: token identifier (default: USDC)
        """
        url = f"{self.base_url}/w3s/developer/transactions/transfer"
        payload = {
            "idempotencyKey": f"transfer-{source_wallet_id}-{destination_address}",
            "source": {
                "type": "wallet",
                "id": source_wallet_id
            },
            "destination": {
                "type": "blockchain",
                "address": destination_address,
                "chain": "ETH-SEPOLIA"  # Adjust based on your needs
            },
            "amount": {
                "amount": amount,
                "currency": token_id
            }
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def batch_transfer(self, source_wallet_id: str, transfers: List[Dict]) -> Dict:
        """
        Batch transfer to multiple addresses
        transfers: List of {destination_address, amount, token_id}
        """
        # Circle API might not support batch transfers directly
        # This is a wrapper that makes multiple transfer calls
        results = []
        for transfer in transfers:
            try:
                result = self.transfer(
                    source_wallet_id,
                    transfer["destination_address"],
                    transfer["amount"],
                    transfer.get("token_id", "USDC")
                )
                results.append({
                    "destination": transfer["destination_address"],
                    "status": "success",
                    "transaction": result
                })
            except Exception as e:
                results.append({
                    "destination": transfer["destination_address"],
                    "status": "failed",
                    "error": str(e)
                })
        return {"results": results}
    
    def get_transaction_status(self, transaction_id: str) -> Dict:
        """Get transaction status"""
        url = f"{self.base_url}/w3s/developer/transactions/{transaction_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


# Global instance
circle_api = CircleAPI()

