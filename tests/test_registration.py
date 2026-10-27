"""
Automated Unit Tests for Registration Cart, Engine & Workflows (Practical 7 & Practical 3-5)
"""

import pytest
from crss.registration import CourseCart, CourseRegistrationEngine, MeritScholarshipPolicy
from crss.models import Student
from crss.exceptions import (
    DuplicateCourseError,
    CreditLimitExceededError,
    SectionNotFoundError,
    PrerequisiteUnmetError,
    TimetableClashError,
    SeatUnavailableError
)


# =========================================================================
# 1. COURSE CART TDD TESTS (Practical 7)
# =========================================================================

def test_add_section_increases_cart_count(sample_sections):
    """Cycle 1: Adding a section increases cart count."""
    cart = CourseCart("25C21510")
    cart.add_section(sample_sections["sec1"])
    assert cart.count == 1
    assert cart.total_credits == 3


def test_calculate_total_credits(sample_sections):
    """Cycle 2: Total academic credits accumulate correctly across multiple sections."""
    cart = CourseCart("25C21510")
    cart.add_section(sample_sections["sec1"])  # 3 cr
    cart.add_section(sample_sections["sec2"])  # 4 cr
    assert cart.total_credits == 7


def test_duplicate_course_code_rejected(sample_sections, sample_courses):
    """Cycle 3: Adding duplicate sections of the same course code is rejected."""
    cart = CourseCart("25C21510")
    cart.add_section(sample_sections["sec1"])  # CS-101 Sec A
    # Attempt to add another section of CS-101
    with pytest.raises(DuplicateCourseError):
        cart.add_section(sample_sections["sec_full"])  # Also CS-101


def test_overload_credit_limit_rejected(sample_sections):
    """Cycle 4: Adding sections beyond maximum credit limit (18 credits) raises error."""
    cart = CourseCart("25C21510", max_credits=6)
    cart.add_section(sample_sections["sec1"])  # 3 cr
    # sec2 has 4 credits -> total would be 7 > 6
    with pytest.raises(CreditLimitExceededError):
        cart.add_section(sample_sections["sec2"])


def test_remove_section_updates_cart(sample_sections):
    """Cycle 5: Removing a section updates count and credits; non-existent raises error."""
    cart = CourseCart("25C21510")
    cart.add_section(sample_sections["sec1"])
    assert cart.count == 1
    cart.remove_section("SEC-101-A")
    assert cart.count == 0
    assert cart.total_credits == 0
    with pytest.raises(SectionNotFoundError):
        cart.remove_section("NON_EXISTENT_ID")


def test_merit_scholarship_discount_policy(sample_sections):
    """Cycle 6: Merit scholarship fee waiver policy applies 10% discount."""
    cart = CourseCart("25C21510")
    cart.add_section(sample_sections["sec1"])  # 15,000 base fee
    cart.add_section(sample_sections["sec2"])  # 15,000 base fee
    # Total base fee = 30,000. 10% discount -> 27,000.
    policy = MeritScholarshipPolicy(discount_pct=10.0)
    tuition = cart.calculate_total_tuition(policy)
    assert tuition == 27000.0


# =========================================================================
# 2. REGISTRATION ENGINE WORKFLOW TESTS
# =========================================================================

def test_atomic_registration_success(student_deep, sample_sections, mock_services):
    """Verifies happy path registration, seat count decrement, and notification."""
    engine = CourseRegistrationEngine(
        sis_service=mock_services["sis"],
        notifier=mock_services["notifier"],
        logger=mock_services["logger"]
    )
    sec = sample_sections["sec2"]  # CS-201
    initial_seats = sec.available_seats

    enrollment = engine.register_section(student_deep, sec)
    assert enrollment is not None
    assert sec.available_seats == initial_seats - 1
    assert sec.section_id in [s.section_id for s in student_deep.timetable.sections]
    mock_services["notifier"].send_email.assert_called_once()
    mock_services["logger"].log_event.assert_called_once()


def test_timetable_clash_detection_blocks_registration(student_deep, sample_sections, mock_services):
    """Verifies that an overlapping schedule causes immediate rejection."""
    engine = CourseRegistrationEngine(
        sis_service=mock_services["sis"],
        notifier=mock_services["notifier"],
        logger=mock_services["logger"]
    )
    # Register first course (Mon 09:00-10:30)
    engine.register_section(student_deep, sample_sections["sec1"])

    # Attempt to register conflicting course (Mon 09:30-11:00)
    with pytest.raises(TimetableClashError):
        engine.register_section(student_deep, sample_sections["sec3_clash"])


def test_prerequisite_unmet_blocks_registration(sample_sections, mock_services):
    """Verifies that missing prerequisite causes registration rejection."""
    mock_services["sis"].get_completed_courses.return_value = []  # No completed courses
    engine = CourseRegistrationEngine(
        sis_service=mock_services["sis"],
        notifier=mock_services["notifier"],
        logger=mock_services["logger"]
    )
    freshman = Student("25C21599", "Freshman Student", "freshman@univ.edu")

    # sec2 is CS-201 which requires CS-101
    with pytest.raises(PrerequisiteUnmetError):
        engine.register_section(freshman, sample_sections["sec2"])


def test_seat_full_blocks_registration(student_deep, sample_sections, mock_services):
    """Verifies that zero available seats blocks registration."""
    engine = CourseRegistrationEngine(
        sis_service=mock_services["sis"],
        notifier=mock_services["notifier"],
        logger=mock_services["logger"]
    )
    full_sec = sample_sections["sec_full"]
    assert full_sec.available_seats == 0

    with pytest.raises(SeatUnavailableError):
        engine.register_section(student_deep, full_sec)


def test_course_drop_workflow_restores_seat(student_deep, sample_sections, mock_services):
    """Verifies that dropping a section restores seat count and updates timetable."""
    engine = CourseRegistrationEngine(
        sis_service=mock_services["sis"],
        notifier=mock_services["notifier"],
        logger=mock_services["logger"]
    )
    sec = sample_sections["sec1"]
    engine.register_section(student_deep, sec)
    seats_after_reg = sec.available_seats

    engine.drop_section(student_deep, sec)
    assert sec.available_seats == seats_after_reg + 1
    assert sec.section_id not in [s.section_id for s in student_deep.timetable.sections]
