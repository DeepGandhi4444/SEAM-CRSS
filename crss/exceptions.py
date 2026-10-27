"""
Course Registration & Scheduling System (CRSS) - Domain Exceptions
"""

class CRSSError(Exception):
    """Base exception for all CRSS domain errors."""
    pass


# Authentication Exceptions
class AuthenticationError(CRSSError):
    """Raised when authentication credentials or token are invalid."""
    pass


class AccountFrozenError(CRSSError):
    """Raised when an operation is blocked due to an administrative or financial hold."""
    pass


# Registration Exceptions
class PrerequisiteUnmetError(CRSSError):
    """Raised when a student has not completed required prerequisite courses."""
    pass


class TimetableClashError(CRSSError):
    """Raised when a candidate course section conflicts with an already registered section."""
    pass


class SeatUnavailableError(CRSSError):
    """Raised when an enrolled section has zero remaining seats."""
    pass


class DuplicateCourseError(CRSSError):
    """Raised when a student attempts to register for multiple sections of the same course."""
    pass


class CreditLimitExceededError(CRSSError):
    """Raised when total registered credits exceed the allowable limit (18 credits)."""
    pass


class SectionNotFoundError(CRSSError):
    """Raised when referencing a section ID that does not exist in offerings or cart."""
    pass


# Billing & Financial Exceptions
class InvalidAmountError(CRSSError, ValueError):
    """Raised when a financial transaction amount is zero or negative."""
    pass


class InsufficientFundsError(CRSSError):
    """Raised when withdrawal or fee debit exceeds available student balance."""
    pass
