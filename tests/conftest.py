"""
Pytest configuration and shared fixtures for CRSS test suite
"""

import pytest
from datetime import time
from unittest.mock import MagicMock

from crss.models import Student, Course, CourseSection, TimeSlot
from crss.services import NotificationService, AuditLoggerService, StudentInfoDatabaseService
from crss.registration import CourseRegistrationEngine
from crss.billing import StudentFeeAccount


@pytest.fixture
def sample_courses():
    """Provides standard test courses."""
    cs101 = Course("CS-101", "Introduction to Programming", credits=3, department="CS", prerequisites=[])
    cs201 = Course("CS-201", "Data Structures & Algorithms", credits=4, department="CS", prerequisites=["CS-101"])
    cs301 = Course("CS-301", "Software Engineering", credits=4, department="CS", prerequisites=["CS-201"])
    return {"CS-101": cs101, "CS-201": cs201, "CS-301": cs301}


@pytest.fixture
def sample_sections(sample_courses):
    """Provides test sections with specific schedules."""
    sec1 = CourseSection("SEC-101-A", sample_courses["CS-101"], "Prof. A", TimeSlot("MON", time(9, 0), time(10, 30)), capacity=60)
    sec2 = CourseSection("SEC-201-A", sample_courses["CS-201"], "Prof. B", TimeSlot("WED", time(11, 0), time(12, 30)), capacity=40)
    sec3 = CourseSection("SEC-301-A", sample_courses["CS-301"], "Prof. C", TimeSlot("MON", time(9, 30), time(11, 0)), capacity=50) # Clashes with sec1
    sec_full = CourseSection("SEC-FULL", sample_courses["CS-101"], "Prof. D", TimeSlot("FRI", time(10, 0), time(11, 30)), capacity=1)
    sec_full.increment_enrollment() # 0 available seats
    return {
        "sec1": sec1,
        "sec2": sec2,
        "sec3_clash": sec3,
        "sec_full": sec_full
    }


@pytest.fixture
def student_deep():
    """Provides authenticated student instance for Deep C. Gandhi."""
    s = Student("25C21510", "Deep C. Gandhi", "25c21510@university.edu", major="Computer Science")
    s.add_completed_course("CS-101")
    s.add_completed_course("CS-201")
    return s


@pytest.fixture
def mock_services():
    """Provides mocked notification and audit logging services."""
    mock_notifier = MagicMock(spec=NotificationService)
    mock_logger = MagicMock(spec=AuditLoggerService)
    mock_sis = MagicMock(spec=StudentInfoDatabaseService)
    mock_sis.get_completed_courses.return_value = ["CS-101", "CS-201"]
    return {
        "notifier": mock_notifier,
        "logger": mock_logger,
        "sis": mock_sis
    }


@pytest.fixture
def fee_account_with_mocks():
    """Provides student fee account wired to mocks."""
    mock_notifier = MagicMock()
    mock_logger = MagicMock()
    account = StudentFeeAccount("25C21510", initial_balance=20000.0, notifier=mock_notifier, logger=mock_logger)
    return account, mock_notifier, mock_logger
