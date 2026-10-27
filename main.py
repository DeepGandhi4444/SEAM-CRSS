"""
Course Registration & Scheduling System (CRSS)
Interactive Demonstration & CLI Application

Student: Deep C. Gandhi | Enrollment: 25C21510
Subject: Software Engineering & Agile Methodology (SEAM)
"""

import sys
from datetime import time
from crss.models import Student, Course, CourseSection, TimeSlot
from crss.auth import authenticate_user
from crss.registration import CourseRegistrationEngine, CourseCart, MeritScholarshipPolicy
from crss.billing import StudentFeeAccount
from crss.services import NotificationService, AuditLoggerService, StudentInfoDatabaseService
from crss.exceptions import CRSSError


def create_demo_catalog():
    """Initializes sample academic catalog and course sections."""
    cs101 = Course("CS-101", "Introduction to Programming", credits=3, department="Computer Science", prerequisites=[], base_fee=12000.0)
    cs201 = Course("CS-201", "Data Structures & Algorithms", credits=4, department="Computer Science", prerequisites=["CS-101"], base_fee=16000.0)
    cs301 = Course("CS-301", "Software Engineering & Agile", credits=4, department="Computer Science", prerequisites=["CS-201"], base_fee=18000.0)
    cs310 = Course("CS-310", "Database Management Systems", credits=3, department="Computer Science", prerequisites=["CS-101"], base_fee=14000.0)
    math220 = Course("MATH-220", "Discrete Mathematics", credits=3, department="Mathematics", prerequisites=[], base_fee=12000.0)

    # Sections with specific timeslots
    sec1 = CourseSection("CS301-A", cs301, "Prof. Sharma", TimeSlot("MON", time(9, 0), time(10, 30), "Lab-201"), capacity=60)
    sec2 = CourseSection("CS310-A", cs310, "Prof. Mehta", TimeSlot("WED", time(11, 0), time(12, 30), "Hall-102"), capacity=50)
    sec3 = CourseSection("MATH220-A", math220, "Prof. Patel", TimeSlot("MON", time(9, 30), time(11, 0), "Room-305"), capacity=45) # Clashes with CS301-A on Mon
    sec4 = CourseSection("CS201-A", cs201, "Prof. Desai", TimeSlot("THU", time(14, 0), time(16, 0), "Lab-105"), capacity=40)

    sections = {
        "CS301-A": sec1,
        "CS310-A": sec2,
        "MATH220-A": sec3,
        "CS201-A": sec4
    }
    return sections


def main():
    print("=" * 76)
    print("   COURSE REGISTRATION & SCHEDULING SYSTEM (CRSS) - V1.0")
    print("   Student: Deep C. Gandhi | Enrollment: 25C21510 | Subject: SEAM")
    print("=" * 76)

    # 1. Authentication
    print("\n[1] AUTHENTICATION DEMO (Practical 6 Dual-Mode Auth)")
    enrollment_no = "25C21510"
    print(f"Authenticating student {enrollment_no} via campus OAuth2 SSO...")
    auth_res = authenticate_user(enrollment_no, "student_secret_pass", auth_mode="SSO")
    print(f" -> Authentication SUCCESS! Token: {auth_res['token']} (Auth Type: {auth_res['auth_type']})")

    # Initialize Services & Student
    sis = StudentInfoDatabaseService()
    notifier = NotificationService()
    logger = AuditLoggerService()
    engine = CourseRegistrationEngine(sis_service=sis, notifier=notifier, logger=logger)

    student = Student(enrollment_no, "Deep C. Gandhi", "25c21510@university.edu", major="Computer Science & Engineering")
    print(f" -> Student Profile Loaded: {student.name} | Major: {student.major}")
    print(f" -> SIS Verified Transcripts: {sis.get_completed_courses(enrollment_no)}")

    # 2. Catalog & Offerings
    sections = create_demo_catalog()
    print("\n[2] AVAILABLE COURSE OFFERINGS:")
    print("-" * 76)
    for sec in sections.values():
        print(f" • {sec}")
    print("-" * 76)

    # 3. Successful Atomic Registration
    print("\n[3] ATOMIC REGISTRATION (Happy Path)")
    target_sec = sections["CS301-A"]
    print(f"Attempting registration for {target_sec.course_code} ({target_sec.section_id})...")
    try:
        enr = engine.register_section(student, target_sec)
        print(f" -> SUCCESS! Confirmed Enrollment ID: {enr.enrollment_id}")
        print(f" -> Available seats updated: {target_sec.available_seats}/{target_sec.capacity}")
    except CRSSError as e:
        print(f" -> FAILED: {e}")

    # Register second non-clashing course
    sec2 = sections["CS310-A"]
    print(f"\nAttempting registration for {sec2.course_code} ({sec2.section_id})...")
    try:
        enr2 = engine.register_section(student, sec2)
        print(f" -> SUCCESS! Confirmed Enrollment ID: {enr2.enrollment_id}")
    except CRSSError as e:
        print(f" -> FAILED: {e}")

    # 4. Timetable Clash Detection Demonstration
    print("\n[4] TIMETABLE CLASH DETECTION DEMO")
    clash_sec = sections["MATH220-A"]  # Scheduled Mon 09:30-11:00 (overlaps with CS301-A Mon 09:00-10:30)
    print(f"Attempting to register for conflicting section {clash_sec.course_code} ({clash_sec.timeslot})...")
    try:
        engine.register_section(student, clash_sec)
    except CRSSError as e:
        print(f" -> BLOCKED AS EXPECTED: {e}")

    # 5. Prerequisite Enforcement Demonstration
    print("\n[5] PREREQUISITE ENFORCEMENT DEMO")
    freshman = Student("25C21599", "New Student", "new.student@univ.edu")
    print(f"Testing freshman {freshman.enrollment_no} attempting to register for advanced CS-301...")
    try:
        engine.register_section(freshman, target_sec)
    except CRSSError as e:
        print(f" -> BLOCKED AS EXPECTED: {e}")

    # 6. Current Student Weekly Timetable View
    print("\n[6] CURRENT ENROLLED WEEKLY TIMETABLE:")
    print("-" * 76)
    for s in student.timetable.sections:
        print(f" [CONFIRMED] {s.course_code} - {s.course.title} | {s.timeslot} | Instructor: {s.instructor}")
    print("-" * 76)

    # 7. Tuition Fee Account & Scholarship Calculation
    print("\n[7] FINANCIAL LEDGER & SCHOLARSHIP TUITION (Practical 7 & 8)")
    fee_account = StudentFeeAccount(student.enrollment_no, initial_balance=50000.0, notifier=notifier, logger=logger)
    print(f"Initial Student Account Balance: Rs. {fee_account.balance:.2f}")

    cart = CourseCart(student.enrollment_no)
    cart.add_section(target_sec)
    cart.add_section(sec2)

    base_tuition = cart.calculate_total_tuition()
    scholarship_policy = MeritScholarshipPolicy(discount_pct=10.0)
    discounted_tuition = cart.calculate_total_tuition(scholarship_policy)

    print(f"Total Academic Credits: {cart.total_credits} cr across {cart.count} sections")
    print(f"Standard Base Tuition: Rs. {base_tuition:.2f}")
    print(f"With Merit Scholarship (10% Waiver): Rs. {discounted_tuition:.2f}")

    print(f"Deducting discounted tuition from student account...")
    fee_account.withdraw(discounted_tuition)
    print(f" -> Final Remaining Account Balance: Rs. {fee_account.balance:.2f}")

    # 8. Notification & Audit Log Summary
    print("\n[8] EXTERNAL SERVICE DISPATCH LOG (Notifications & Audit Trail):")
    print("-" * 76)
    for notif in notifier.sent_notifications:
        print(f" [{notif['channel']}] To: {notif['recipient']} | Subject: {notif['subject']}")
    print(f"Total Audit Trail Entries Logged: {len(logger.audit_log)}")
    print("-" * 76)

    print("\n[SUCCESS] End-to-End CRSS demonstration completed successfully!")
    print("To run the full automated test suite, execute: pytest -v")


if __name__ == "__main__":
    main()
