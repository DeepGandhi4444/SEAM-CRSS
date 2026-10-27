"""
Course Registration & Scheduling System (CRSS) - Registration Engine & Cart
Implements Practical 7 TDD Architecture and Practical 3 & 4 Business Workflows
"""

from typing import Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from crss.models import Student, CourseSection, Enrollment, EnrollmentStatus
from crss.services import NotificationService, AuditLoggerService, StudentInfoDatabaseService
from crss.exceptions import (
    DuplicateCourseError,
    CreditLimitExceededError,
    SectionNotFoundError,
    PrerequisiteUnmetError,
    TimetableClashError,
    SeatUnavailableError
)


# =========================================================================
# STRATEGY PATTERN FOR TUITION & SCHOLARSHIPS (Practical 7 Cycle 6)
# =========================================================================

class PricingPolicy(ABC):
    """Abstract Strategy interface for tuition fee calculation."""
    @abstractmethod
    def calculate_discount(self, base_total: float) -> float:
        pass


class StandardPricingPolicy(PricingPolicy):
    def calculate_discount(self, base_total: float) -> float:
        return 0.0


class MeritScholarshipPolicy(PricingPolicy):
    """Merit scholarship fee waiver policy (10% discount)."""
    def __init__(self, discount_pct: float = 10.0):
        self.discount_pct = discount_pct

    def calculate_discount(self, base_total: float) -> float:
        return round(base_total * (self.discount_pct / 100.0), 2)


# =========================================================================
# COURSE REGISTRATION CART (Practical 7 TDD Micro-Cycles 1-6)
# =========================================================================

class CourseCart:
    """
    Manages student's staged course sections prior to final registration commit.
    Enforces credit limit and uniqueness constraints.
    """
    def __init__(self, student_id: str, max_credits: int = 18):
        self.student_id = student_id
        self.max_credits = max_credits
        self._sections: Dict[str, CourseSection] = {}

    @property
    def total_credits(self) -> int:
        return sum(s.credits for s in self._sections.values())

    @property
    def count(self) -> int:
        return len(self._sections)

    @property
    def items(self) -> List[CourseSection]:
        return list(self._sections.values())

    def add_section(self, section: CourseSection):
        """Adds section to cart with duplicate course and credit limit checks."""
        if any(s.course_code == section.course_code for s in self._sections.values()):
            raise DuplicateCourseError(f"Course {section.course_code} is already in cart.")
        if self.total_credits + section.credits > self.max_credits:
            raise CreditLimitExceededError(
                f"Adding {section.course_code} ({section.credits} cr) exceeds the {self.max_credits} max credit ceiling."
            )
        self._sections[section.section_id] = section

    def remove_section(self, section_id: str):
        """Removes a section from cart."""
        if section_id not in self._sections:
            raise SectionNotFoundError(f"Section {section_id} not found in cart.")
        del self._sections[section_id]

    def clear(self):
        self._sections.clear()

    def calculate_total_tuition(self, pricing_policy: Optional[PricingPolicy] = None) -> float:
        """Calculates total tuition applying active pricing policy."""
        base_fee = sum(s.base_fee for s in self._sections.values())
        policy = pricing_policy or StandardPricingPolicy()
        discount = policy.calculate_discount(base_fee)
        return round(base_fee - discount, 2)


# =========================================================================
# REGISTRATION COORDINATION ENGINE
# =========================================================================

class CourseRegistrationEngine:
    """
    Coordinates atomic validation, seat allocation, prerequisite verification,
    schedule conflict checks, and asynchronous notification dispatch.
    """
    def __init__(self,
                 sis_service: Optional[StudentInfoDatabaseService] = None,
                 notifier: Optional[NotificationService] = None,
                 logger: Optional[AuditLoggerService] = None):
        self.sis = sis_service or StudentInfoDatabaseService()
        self.notifier = notifier or NotificationService()
        self.logger = logger or AuditLoggerService()
        self.enrollments: List[Enrollment] = []

    def validate_prerequisites(self, student: Student, section: CourseSection) -> bool:
        """Verifies student has completed all required prerequisite courses."""
        prereqs = section.course.prerequisites
        if not prereqs:
            return True
        completed = set(self.sis.get_completed_courses(student.enrollment_no))
        missing = [p for p in prereqs if p not in completed]
        if missing:
            raise PrerequisiteUnmetError(
                f"Prerequisite course(s) missing for {section.course_code}: {', '.join(missing)}."
            )
        return True

    def register_section(self, student: Student, section: CourseSection) -> Enrollment:
        """
        Executes atomic enrollment:
        1. Check seat availability
        2. Validate prerequisites via SIS
        3. Check timetable conflict
        4. Increment enrolled count
        5. Add to student timetable
        6. Dispatch notification & log audit
        """
        # Step 1: Seat Availability
        if not section.has_available_seat():
            raise SeatUnavailableError(f"Section {section.section_id} has no available seats remaining.")

        # Step 2: Prerequisites
        self.validate_prerequisites(student, section)

        # Step 3: Timetable Clash
        clash = student.timetable.check_clash(section)
        if clash:
            raise TimetableClashError(
                f"Schedule conflict: {section.course_code} ({section.timeslot}) overlaps with registered {clash.course_code} ({clash.timeslot})."
            )

        # Step 4: Atomic Seat Increment & Timetable Update
        section.increment_enrollment()
        student.timetable.add_section(section)

        # Step 5: Enrollment Record
        eid = f"ENR-{student.enrollment_no}-{section.section_id}-{int(datetime.now().timestamp())}"
        enrollment = Enrollment(enrollment_id=eid, student_id=student.enrollment_no, section_id=section.section_id)
        self.enrollments.append(enrollment)

        # Step 6: Asynchronous Confirmation & Audit
        self.notifier.send_email(
            student.email,
            f"Registration Confirmed: {section.course_code} ({section.section_id})",
            f"Dear {student.name}, you are confirmed in {section.course.title} at {section.timeslot}."
        )
        self.logger.log_event("ENROLLMENT_SUCCESS", student.enrollment_no, f"Registered {section.section_id}")

        return enrollment

    def drop_section(self, student: Student, section: CourseSection, deadline: Optional[datetime] = None) -> bool:
        """Drops an enrolled section, restores available seat, and updates timetable."""
        now = datetime.now()
        if deadline and now > deadline:
            raise TimeoutError("Drop request rejected: The official Add/Drop deadline has passed.")

        student.timetable.remove_section(section.section_id)
        section.decrement_enrollment()

        self.notifier.send_email(
            student.email,
            f"Course Dropped: {section.course_code} ({section.section_id})",
            f"You have dropped {section.course.title}."
        )
        self.logger.log_event("COURSE_DROP", student.enrollment_no, f"Dropped {section.section_id}")
        return True
