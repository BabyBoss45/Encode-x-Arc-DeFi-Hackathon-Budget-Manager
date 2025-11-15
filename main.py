from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------- Mock ERC20 Interface (for simulation) ----------
# dfdf[dfdf
class MockERC20:
    """
    Very simple in-memory ERC20-like token.
    Only for tests/simulation – not real blockchain code.
    """
    def __init__(self, name="MockUSDC", symbol="USDC", decimals=6):
        self.name = name
        self.symbol = symbol
        self._decimals = decimals
        self.balances: Dict[str, int] = {}

    def decimals(self) -> int:
        return self._decimals

    def balanceOf(self, account: str) -> int:
        return self.balances.get(account, 0)

    def _mint(self, to: str, amount: int):
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self.balances[to] = self.balanceOf(to) + amount

    def transfer(self, sender: str, to: str, amount: int) -> bool:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if self.balanceOf(sender) < amount:
            raise ValueError("insufficient balance")
        if to is None:
            raise ValueError("zero address")

        self.balances[sender] -= amount
        self.balances[to] = self.balanceOf(to) + amount
        return True


# ---------- Data Structures ----------

@dataclass
class Department:
    name: str
    active: bool = True


@dataclass
class Worker:
    name: str
    department_id: int
    wallet: str
    salary: int              # in smallest unit (e.g. 6 decimals for USDC)
    active: bool = True


# ---------- Main Treasury & Payroll Logic ----------

class ArcTreasuryPayroll:
    """
    Python translation of the Solidity ArcTreasuryPayroll contract.
    Simulates:
      - departments
      - workers
      - USDC treasury
      - payroll
      - pause/owner checks
      - event emission (as logs)
    """

    def __init__(self, usdc: MockERC20, owner: str):
        if usdc is None:
            raise ValueError("USDC cannot be None")
        self.usdc = usdc

        # Ownership / pause
        self.owner: str = owner
        self.paused: bool = False

        # IDs
        self.next_department_id: int = 1
        self.next_worker_id: int = 1

        # Storage
        self.departments: Dict[int, Department] = {}
        self.workers: Dict[int, Worker] = {}
        self.department_workers: Dict[int, List[int]] = {}

        # Event log (list of tuples or dicts)
        self.events: List[dict] = []

    # ---------- Internal helpers ----------

    def _only_owner(self, caller: str):
        if caller != self.owner:
            raise PermissionError("Not owner")

    def _when_not_paused(self):
        if self.paused:
            raise RuntimeError("Contract is paused")

    def _valid_department(self, department_id: int):
        dept = self.departments.get(department_id)
        if dept is None or not dept.active:
            raise ValueError("Invalid/Inactive department")

    def _valid_worker(self, worker_id: int):
        worker = self.workers.get(worker_id)
        if worker is None or worker.wallet is None:
            raise ValueError("Worker does not exist")

    def _emit(self, event_name: str, **kwargs):
        self.events.append({"event": event_name, **kwargs})

    # ---------- Ownership / pause ----------

    def transfer_ownership(self, caller: str, new_owner: str):
        self._only_owner(caller)
        if new_owner is None:
            raise ValueError("Zero address for new owner")
        old_owner = self.owner
        self.owner = new_owner
        self._emit("OwnershipTransferred", previousOwner=old_owner, newOwner=new_owner)

    def pause(self, caller: str):
        self._only_owner(caller)
        if self.paused:
            raise RuntimeError("Already paused")
        self.paused = True
        self._emit("Paused", account=caller)

    def unpause(self, caller: str):
        self._only_owner(caller)
        if not self.paused:
            raise RuntimeError("Not paused")
        self.paused = False
        self._emit("Unpaused", account=caller)

    # ---------- Treasury functions ----------

    def treasury_balance(self, self_address: str) -> int:
        """Return current USDC balance held by this 'contract' address."""
        return self.usdc.balanceOf(self_address)

    def record_deposit(self, caller: str, amount: int):
        """
        In Solidity version, funds are already transferred to the contract address.
        This just emits an event for backend clarity.
        """
        self._only_owner(caller)
        if amount <= 0:
            raise ValueError("Amount must be > 0")
        self._emit("TreasuryDeposit", from_addr=caller, amount=amount)

    def withdraw_treasury(self, caller: str, from_address: str, to: str, amount: int):
        """
        Simulate treasury withdrawal: transfer USDC from 'contract address' to 'to'.
        In Solidity, 'from_address' would be address(this).
        """
        self._only_owner(caller)
        self._when_not_paused()

        if to is None:
            raise ValueError("Zero address for recipient")
        if amount <= 0:
            raise ValueError("Amount must be > 0")

        # simulate ERC20 transfer from contract to 'to'
        self.usdc.transfer(from_address, to, amount)
        self._emit("TreasuryWithdrawal", to=to, amount=amount)

    # ---------- Department management ----------

    def create_department(self, caller: str, name: str) -> int:
        self._only_owner(caller)
        self._when_not_paused()

        if not name:
            raise ValueError("Department name cannot be empty")

        department_id = self.next_department_id
        self.next_department_id += 1

        self.departments[department_id] = Department(name=name, active=True)
        self.department_workers[department_id] = []

        self._emit("DepartmentCreated", departmentId=department_id, name=name)
        return department_id

    def update_department(self, caller: str, department_id: int, name: str, active: bool):
        self._only_owner(caller)
        self._when_not_paused()

        dept = self.departments.get(department_id)
        if dept is None:
            raise ValueError("Department does not exist")

        if not name:
            raise ValueError("Department name cannot be empty")

        dept.name = name
        dept.active = active

        self._emit(
            "DepartmentUpdated",
            departmentId=department_id,
            name=name,
            active=active
        )

    # ---------- Worker management ----------

    def add_worker(
        self,
        caller: str,
        name: str,
        department_id: int,
        wallet: str,
        salary: int,
    ) -> int:
        self._only_owner(caller)
        self._when_not_paused()
        self._valid_department(department_id)

        if wallet is None:
            raise ValueError("Zero wallet address")
        if salary <= 0:
            raise ValueError("Salary must be > 0")
        if not name:
            raise ValueError("Worker name cannot be empty")

        worker_id = self.next_worker_id
        self.next_worker_id += 1

        worker = Worker(
            name=name,
            department_id=department_id,
            wallet=wallet,
            salary=salary,
            active=True,
        )
        self.workers[worker_id] = worker
        self.department_workers.setdefault(department_id, []).append(worker_id)

        self._emit(
            "WorkerAdded",
            workerId=worker_id,
            name=name,
            departmentId=department_id,
            wallet=wallet,
            salary=salary,
        )
        return worker_id

    def update_worker(
        self,
        caller: str,
        worker_id: int,
        name: str,
        department_id: int,
        wallet: str,
        salary: int,
        active: bool,
    ):
        self._only_owner(caller)
        self._when_not_paused()
        self._valid_worker(worker_id)
        self._valid_department(department_id)

        if wallet is None:
            raise ValueError("Zero wallet")
        if salary <= 0:
            raise ValueError("Salary must be > 0")
        if not name:
            raise ValueError("Worker name cannot be empty")

        w = self.workers[worker_id]

        # if department changed, move worker between department lists
        if w.department_id != department_id:
            # remove from old
            old_list = self.department_workers.get(w.department_id, [])
            if worker_id in old_list:
                old_list.remove(worker_id)
            # add to new
            self.department_workers.setdefault(department_id, []).append(worker_id)

        w.name = name
        w.department_id = department_id
        w.wallet = wallet
        w.salary = salary
        w.active = active

        self._emit(
            "WorkerUpdated",
            workerId=worker_id,
            name=name,
            departmentId=department_id,
            wallet=wallet,
            salary=salary,
            active=active,
        )

    def deactivate_worker(self, caller: str, worker_id: int):
        self._only_owner(caller)
        self._when_not_paused()
        self._valid_worker(worker_id)

        w = self.workers[worker_id]
        w.active = False

        self._emit(
            "WorkerUpdated",
            workerId=worker_id,
            name=w.name,
            departmentId=w.department_id,
            wallet=w.wallet,
            salary=w.salary,
            active=False,
        )

    # ---------- Payroll ----------

    def run_payroll(
        self,
        caller: str,
        self_address: str,
        worker_ids: List[int],
    ):
        """
        Simulates runPayroll in Solidity:
        - calculates total salary for all active workers in worker_ids
        - checks treasury balance
        - transfers USDC to each worker's wallet
        - emits SalaryPaid for each
        """
        self._only_owner(caller)
        self._when_not_paused()

        # Calculate total
        total_required = 0
        for worker_id in worker_ids:
            worker = self.workers.get(worker_id)
            if worker and worker.active and worker.wallet is not None and worker.salary > 0:
                total_required += worker.salary

        if self.usdc.balanceOf(self_address) < total_required:
            raise ValueError("Insufficient USDC in treasury")

        # Pay one-by-one
        for worker_id in worker_ids:
            worker = self.workers.get(worker_id)
            if not worker:
                continue
            if not worker.active or worker.wallet is None or worker.salary <= 0:
                continue

            # simulate transfer from contract address to worker.wallet
            self.usdc.transfer(self_address, worker.wallet, worker.salary)
            self._emit(
                "SalaryPaid",
                workerId=worker_id,
                wallet=worker.wallet,
                amount=worker.salary,
                departmentId=worker.department_id,
            )

    # ---------- View helpers ----------

    def get_department_workers(self, department_id: int) -> List[int]:
        return list(self.department_workers.get(department_id, []))

    def get_worker(self, worker_id: int) -> Optional[Worker]:
        return self.workers.get(worker_id)

    def get_department(self, department_id: int) -> Optional[Department]:
        return self.departments.get(department_id)
