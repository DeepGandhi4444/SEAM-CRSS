"""
Course Registration & Scheduling System (CRSS) - Student Fee Account & Billing
Implements Practical 8: Unit Testing with Boundary Value Analysis, Equivalence Partitioning & Mocks
"""

from typing import Optional
from crss.exceptions import InvalidAmountError, InsufficientFundsError, AccountFrozenError
from crss.services import NotificationService, AuditLoggerService


class StudentFeeAccount:
    """
    Manages student tuition ledger, fee deductions, deposits, and financial holds.
    Designed with dependency injection to allow mocking of external notification and audit gateways.
    """
    def __init__(self,
                 student_id: str,
                 initial_balance: float = 0.0,
                 notifier: Optional[NotificationService] = None,
                 logger: Optional[AuditLoggerService] = None):
        self.student_id = student_id
        self._balance = round(float(initial_balance), 2)
        self._is_frozen = False
        self.notifier = notifier
        self.logger = logger

    @property
    def balance(self) -> float:
        """Returns verified student account balance."""
        return self._balance

    @property
    def is_frozen(self) -> bool:
        """Indicates whether an administrative financial hold is active."""
        return self._is_frozen

    def freeze_account(self):
        """Places financial hold on account, blocking transactions."""
        self._is_frozen = True

    def unfreeze_account(self):
        """Removes financial hold."""
        self._is_frozen = False

    def deposit(self, amount: float):
        """Credits tuition funds to student account with notification and audit."""
        if self._is_frozen:
            raise AccountFrozenError(f"Account {self.student_id} is frozen due to an administrative hold.")
        if amount <= 0.0:
            raise InvalidAmountError("Deposit amount must be strictly greater than 0.00.")

        self._balance = round(self._balance + amount, 2)

        # Notify via injected external gateway (mockable in unit testing)
        if self.notifier:
            try:
                self.notifier.send_email(
                    f"{self.student_id.lower()}@univ.edu",
                    f"Deposit Confirmed: {amount:.2f}",
                    f"Your account balance is now Rs. {self._balance:.2f}."
                )
            except Exception:
                # Resilient error handling: Do not roll back a valid deposit if email gateway is down
                pass

        if self.logger:
            self.logger.log_event("TX_DEPOSIT", self.student_id, f"Deposited {amount:.2f}")

    def withdraw(self, amount: float):
        """Debits tuition fee from student account."""
        if self._is_frozen:
            raise AccountFrozenError(f"Account {self.student_id} is frozen due to an administrative hold.")
        if amount <= 0.0:
            raise InvalidAmountError("Withdrawal amount must be strictly greater than 0.00.")
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds: Attempted to withdraw {amount:.2f} with balance {self._balance:.2f}."
            )

        self._balance = round(self._balance - amount, 2)

        if self.notifier:
            try:
                self.notifier.send_email(
                    f"{self.student_id.lower()}@univ.edu",
                    f"Fee Deducted: {amount:.2f}",
                    f"Remaining balance: Rs. {self._balance:.2f}."
                )
            except Exception:
                pass

        if self.logger:
            self.logger.log_event("TX_WITHDRAW", self.student_id, f"Withdrew {amount:.2f}")
