"""
Course Registration & Scheduling System (CRSS) - Domain Models
Corresponds directly to Practical 3 UML Class Diagram & Practical 2 IEEE 830 SRS
"""

from datetime import datetime, time
from typing import List, Dict, Optional
from enum import Enum
from crss.exceptions import TimetableClashError, SeatUnavailableError


class UserRole(Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    ADMINISTRATOR = "ADMINISTRATOR"


class EnrollmentStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    DROPPED = "DROPPED"
    WAITLISTED = "WAITLISTED"


class TimeSlot:
    """Represents a scheduled lecture or lab timing."""
    def __init__(self, day_of_week: str, start_time: time, end_time: time, room: str = "TBD"):
        self.day_of_week = day_of_week.upper()  # e.g., MON, TUE, WED, THU, FRI
        self.start_time = start_time
        self.end_time = end_time
        self.room = room

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """
        Determines if two timeslots have a temporal clash on the same day.
        Zero-gap back-to-back classes (e.g. 10:30 end and 10:30 start) are allowed.
        """
        if self.day_of_week != other.day_of_week:
            return False
        # Overlap occurs when start of A is before end of B AND end of A is after start of B
        return max(self.start_time, other.start_time) < min(self.end_time, other.end_time)

    def __str__(self) -> str:
        return f"{self.day_of_week} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} ({self.room})"


class Course:
    """Represents a master academic course offering."""
    def __init__(self, course_code: str, title: str, credits: int, department: str, prerequisites: Optional[List[str]] = None, base_fee: float = 15000.0):
        self.course_code = course_code.upper()
        self.title = title
        self.credits = credits
        self.department = department
        self.prerequisites = prerequisites or []
        self.base_fee = base_fee

    def add_prerequisite(self, prereq_code: str):
        if prereq_code.upper() not in self.prerequisites:
            self.prerequisites.append(prereq_code.upper())


class CourseSection:
    """Represents an active section instance of a course with specific timeslot and capacity."""
    def __init__(self, section_id: str, course: Course, instructor: str, timeslot: TimeSlot, capacity: int = 60):
        self.section_id = section_id
        self.course = course
        self.instructor = instructor
        self.timeslot = timeslot
        self.capacity = capacity
        self.enrolled_count = 0

    @property
    def course_code(self) -> str:
        return self.course.course_code

    @property
    def credits(self) -> int:
        return self.course.credits

    @property
    def base_fee(self) -> float:
        return self.course.base_fee

    @property
    def available_seats(self) -> int:
        return max(0, self.capacity - self.enrolled_count)

    def has_available_seat(self) -> bool:
        return self.available_seats > 0

    def increment_enrollment(self) -> bool:
        """Atomically increments enrollment count if space exists."""
        if not self.has_available_seat():
            raise SeatUnavailableError(f"Section {self.section_id} is completely full (capacity {self.capacity}).")
        self.enrolled_count += 1
        return True

    def decrement_enrollment(self) -> bool:
        """Decrements enrollment count when a course is dropped."""
        if self.enrolled_count > 0:
            self.enrolled_count -= 1
            return True
        return False

    def __str__(self) -> str:
        return f"[{self.section_id}] {self.course_code}: {self.course.title} ({self.credits} cr) | {self.instructor} | {self.timeslot} | Seats: {self.available_seats}/{self.capacity}"


class Timetable:
    """Personalized weekly timetable for an enrolled student."""
    def __init__(self, student_id: str, semester: str = "Fall 2026"):
        self.student_id = student_id
        self.semester = semester
        self._sections: Dict[str, CourseSection] = {}

    @property
    def sections(self) -> List[CourseSection]:
        return list(self._sections.values())

    def check_clash(self, candidate_section: CourseSection) -> Optional[CourseSection]:
        """
        Checks if candidate section clashes with any already registered section.
        Returns conflicting section if clash exists, else None.
        """
        for enrolled in self._sections.values():
            if candidate_section.timeslot.overlaps_with(enrolled.timeslot):
                return enrolled
        return None

    def add_section(self, section: CourseSection):
        clash = self.check_clash(section)
        if clash:
            raise TimetableClashError(
                f"Timetable conflict: Section {section.section_id} ({section.timeslot}) clashes with {clash.section_id} ({clash.timeslot})."
            )
        self._sections[section.section_id] = section

    def remove_section(self, section_id: str):
        if section_id in self._sections:
            del self._sections[section_id]


class User:
    """Base user identity in the CRSS academic platform."""
    def __init__(self, user_id: str, name: str, email: str, role: UserRole):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.is_authenticated = False

    def login(self) -> bool:
        self.is_authenticated = True
        return True

    def logout(self):
        self.is_authenticated = False


class Student(User):
    """Enrolled student user."""
    def __init__(self, enrollment_no: str, name: str, email: str, major: str = "Computer Science"):
        super().__init__(user_id=enrollment_no, name=name, email=email, role=UserRole.STUDENT)
        self.enrollment_no = enrollment_no
        self.major = major
        self.completed_courses: List[str] = []
        self.timetable = Timetable(student_id=enrollment_no)

    def add_completed_course(self, course_code: str):
        if course_code.upper() not in self.completed_courses:
            self.completed_courses.append(course_code.upper())


class Faculty(User):
    """Instructional faculty member."""
    def __init__(self, faculty_id: str, name: str, email: str, department: str):
        super().__init__(user_id=faculty_id, name=name, email=email, role=UserRole.FACULTY)
        self.faculty_id = faculty_id
        self.department = department
        self.assigned_sections: List[CourseSection] = []


class Administrator(User):
    """Privileged academic administrator."""
    def __init__(self, admin_id: str, name: str, email: str, access_level: int = 1):
        super().__init__(user_id=admin_id, name=name, email=email, role=UserRole.ADMINISTRATOR)
        self.admin_id = admin_id
        self.access_level = access_level


class Enrollment:
    """Captures transactional record of course enrollment."""
    def __init__(self, enrollment_id: str, student_id: str, section_id: str):
        self.enrollment_id = enrollment_id
        self.student_id = student_id
        self.section_id = section_id
        self.timestamp = datetime.now()
        self.status = EnrollmentStatus.CONFIRMED
