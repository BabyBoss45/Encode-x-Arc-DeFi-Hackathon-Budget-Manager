"""
API Client for connecting frontend to backend API
"""
import requests
import os
from typing import Optional, Dict, List

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """Set JWT token for authenticated requests"""
        self.token = token
    
    def _get_headers(self) -> Dict:
        """Get request headers with auth token if available"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    # Auth methods
    def register(self, email: str, password: str, company_name: str) -> Dict:
        """Register new user"""
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password, "company_name": company_name}
        )
        response.raise_for_status()
        data = response.json()
        if "access_token" in data:
            self.set_token(data["access_token"])
        return data
    
    def login(self, email: str, password: str) -> Dict:
        """Login user"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        if "access_token" in data:
            self.set_token(data["access_token"])
        return data
    
    # Company methods
    def get_company(self) -> Dict:
        """Get company info"""
        response = requests.get(
            f"{self.base_url}/company/",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def set_master_wallet(self, wallet_address: str, payroll_date: Optional[str] = None, payroll_time: Optional[str] = None) -> Dict:
        """Set master wallet address with optional payroll date and time"""
        response = requests.put(
            f"{self.base_url}/company/master-wallet",
            json={
                "master_wallet_address": wallet_address,
                "payroll_date": payroll_date,
                "payroll_time": payroll_time
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Department methods
    def get_departments(self) -> List[Dict]:
        """Get all departments"""
        response = requests.get(
            f"{self.base_url}/departments/",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_department(self, name: str) -> Dict:
        """Create department"""
        response = requests.post(
            f"{self.base_url}/departments/",
            json={"name": name},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Worker methods
    def get_workers(self, department_id: Optional[int] = None) -> List[Dict]:
        """Get all workers"""
        params = {}
        if department_id:
            params["department_id"] = department_id
        response = requests.get(
            f"{self.base_url}/workers/",
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_worker(self, name: str, surname: str, salary: float, wallet: str, department_id: int) -> Dict:
        """Create worker"""
        response = requests.post(
            f"{self.base_url}/workers/",
            json={
                "name": name,
                "surname": surname,
                "salary": salary,
                "wallet_address": wallet,
                "department_id": department_id
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Spending methods
    def get_spendings(self, department_id: Optional[int] = None) -> List[Dict]:
        """Get all spendings"""
        params = {}
        if department_id:
            params["department_id"] = department_id
        response = requests.get(
            f"{self.base_url}/spendings/",
            params=params,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_spending(self, name: str, amount: float, wallet: str, department_id: Optional[int] = None) -> Dict:
        """Create spending"""
        response = requests.post(
            f"{self.base_url}/spendings/",
            json={
                "name": name,
                "amount": amount,
                "wallet_address": wallet,
                "department_id": department_id
            },
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def update_spending_date(self, spending_id: int, date: str) -> Dict:
        """Update spending date (created_at)"""
        response = requests.patch(
            f"{self.base_url}/spendings/{spending_id}/date",
            json={"date": date},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Revenue methods
    def get_revenues(self) -> List[Dict]:
        """Get all revenues"""
        response = requests.get(
            f"{self.base_url}/revenue/",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def create_revenue(self, amount: float, month: int, year: int) -> Dict:
        """Create revenue"""
        response = requests.post(
            f"{self.base_url}/revenue/",
            json={"amount": amount, "month": month, "year": year},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Dashboard methods
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        response = requests.get(
            f"{self.base_url}/dashboard/stats",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    # Payroll methods
    def execute_payroll(self, period_start: str, period_end: str) -> List[Dict]:
        """Execute payroll"""
        response = requests.post(
            f"{self.base_url}/payroll/execute",
            json={"period_start": period_start, "period_end": period_end},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_payroll_transactions(self) -> List[Dict]:
        """Get all payroll transactions"""
        response = requests.get(
            f"{self.base_url}/payroll/transactions",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()


# Global API client instance
api_client = APIClient()

