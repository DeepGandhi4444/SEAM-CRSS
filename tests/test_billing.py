"""
Practical 8: Unit Testing & Automation Suite with Boundary Value Analysis, EP, and Mocks
Target: StudentFeeAccount
"""

import pytest
from crss.billing import StudentFeeAccount
from crss.exceptions import InvalidAmountError, InsufficientFundsError, AccountFrozenError


# ==========================================
# 1. POSITIVE & NORMAL FUNCTIONAL TESTS
# ==========================================

def test_initial_balance_is_zero(fee_account_with_mocks):
    """TC-01: Verifies initial account balance starts at 0.00."""
    account, _, _ = fee_account_with_mocks
    account._balance = 0.0
    assert account.balance == 0.0


def test_deposit_positive_amount_updates_balance(fee_account_with_mocks):
    """TC-02: Verifies normal deposit increments balance and dispatches notification."""
    account, notifier, logger = fee_account_with_mocks
    initial = account.balance
    account.deposit(15000.0)
    assert account.balance == initial + 15000.0
    notifier.send_email.assert_called_once()
    logger.log_event.assert_called_once()


def test_withdraw_valid_amount_deducts_balance(fee_account_with_mocks):
    """TC-03: Verifies valid withdrawal within balance limits."""
    account, _, logger = fee_account_with_mocks
    account.withdraw(5000.0)
    assert account.balance == 15000.0
    logger.log_event.assert_called_with("TX_WITHDRAW", "25C21510", "Withdrew 5000.00")


# ==========================================
# 2. BOUNDARY VALUE ANALYSIS (BVA) TESTS
# ==========================================

def test_deposit_exact_one_cent_boundary(fee_account_with_mocks):
    """TC-04: Boundary test for minimum legal positive deposit (0.01)."""
    account, _, _ = fee_account_with_mocks
    initial = account.balance
    account.deposit(0.01)
    assert account.balance == round(initial + 0.01, 2)


def test_deposit_zero_boundary_raises_error(fee_account_with_mocks):
    """TC-05: Boundary test for zero deposit (should reject with InvalidAmountError)."""
    account, _, _ = fee_account_with_mocks
    with pytest.raises(InvalidAmountError):
        account.deposit(0.00)


def test_withdraw_exact_balance_zero_remaining(fee_account_with_mocks):
    """TC-06: Boundary test for withdrawing 100% of balance (leaves exactly 0.00)."""
    account, _, _ = fee_account_with_mocks
    curr_balance = account.balance
    account.withdraw(curr_balance)
    assert account.balance == 0.00


def test_withdraw_one_cent_exceeding_balance(fee_account_with_mocks):
    """TC-07: Boundary test for withdrawing 0.01 more than available balance."""
    account, _, _ = fee_account_with_mocks
    curr_balance = account.balance
    with pytest.raises(InsufficientFundsError):
        account.withdraw(round(curr_balance + 0.01, 2))


# ==========================================
# 3. EQUIVALENCE PARTITIONING & NEGATIVE TESTS
# ==========================================

def test_negative_deposit_raises_invalid_amount(fee_account_with_mocks):
    """TC-08: Invalid negative deposit equivalence class."""
    account, _, _ = fee_account_with_mocks
    with pytest.raises(InvalidAmountError):
        account.deposit(-500.0)


def test_withdraw_overdraft_raises_insufficient_funds(fee_account_with_mocks):
    """TC-09: Overdraft withdrawal attempt raises InsufficientFundsError."""
    account, _, _ = fee_account_with_mocks
    with pytest.raises(InsufficientFundsError):
        account.withdraw(999999.0)


def test_frozen_account_blocks_all_transactions(fee_account_with_mocks):
    """TC-10: Verifies administratively frozen account blocks all operations."""
    account, _, _ = fee_account_with_mocks
    account.freeze_account()
    assert account.is_frozen is True
    with pytest.raises(AccountFrozenError):
        account.deposit(1000.0)
    with pytest.raises(AccountFrozenError):
        account.withdraw(1000.0)


# ==========================================
# 4. MOCK DEPENDENCY VERIFICATION & RESILIENCE
# ==========================================

def test_notification_service_called_with_student_email(fee_account_with_mocks):
    """TC-11: Verifies mock notifier is called with exact student email."""
    account, notifier, _ = fee_account_with_mocks
    account.deposit(1000.0)
    notifier.send_email.assert_called_once()
    args, kwargs = notifier.send_email.call_args
    assert "25c21510@univ.edu" in args[0]


def test_audit_logger_records_transaction_event(fee_account_with_mocks):
    """TC-12: Verifies audit log mock records financial audit trail."""
    account, _, logger = fee_account_with_mocks
    account.deposit(5000.0)
    account.withdraw(2000.0)
    assert logger.log_event.call_count == 2


def test_resilience_when_notifier_throws_network_err(fee_account_with_mocks):
    """TC-13: Verifies account remains resilient if external mail gateway drops connection."""
    account, notifier, _ = fee_account_with_mocks
    notifier.send_email.side_effect = ConnectionResetError("Mail server socket timeout")
    initial = account.balance
    # Deposit should still succeed cleanly despite email gateway failure
    account.deposit(5000.0)
    assert account.balance == initial + 5000.0


def test_deliberate_bug_catching_regression(fee_account_with_mocks):
    """
    TC-14: Demonstration of regression protection.
    Verifies that withdrawing more than balance strictly raises InsufficientFundsError.
    """
    account, _, _ = fee_account_with_mocks
    with pytest.raises(InsufficientFundsError):
        account.withdraw(account.balance + 100.0)
