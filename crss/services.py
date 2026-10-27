"""
Course Registration & Scheduling System (CRSS) - External Supporting Services
Implements secondary system integrations for Practical 3 and Mocking targets for Practical 8
"""

from typing import List, Dict, Any
from datetime import datetime


class NotificationService:
    """Asynchronous notification gateway dispatching registration receipts."""
    def __init__(self):
        self.sent_notifications: List[Dict[str, Any]] = []

    def send_email(self, recipient_email: str, subject: str, message: str = "") -> bool:
        """Transmits student confirmation email receipt."""
        record = {
            "recipient": recipient_email,
            "subject": subject,
            "message": message,
            "timestamp": datetime.now(),
            "channel": "EMAIL",
            "status": "DELIVERED"
        }
        self.sent_notifications.append(record)
        return True

    def send_sms(self, phone: str, text: str) -> bool:
        record = {
            "recipient": phone,
            "message": text,
            "timestamp": datetime.now(),
            "channel": "SMS",
            "status": "DELIVERED"
        }
        self.sent_notifications.append(record)
        return True


class AuditLoggerService:
    """Enterprise audit logger recording compliance events."""
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def log_event(self, event_type: str, actor_id: str, details: str, status: str = "SUCCESS"):
        entry = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "actor_id": actor_id,
            "details": details,
            "status": status
        }
        self.audit_log.append(entry)


class StudentInfoDatabaseService:
    """Simulates central University Student Information System (SIS)."""
    def __init__(self):
        # In-memory student transcript records
        self._transcripts: Dict[str, List[str]] = {
            "25C21510": ["CS-101", "CS-201", "MATH-101", "MATH-201"],  # Deep C. Gandhi completed prereqs
            "25C21511": ["CS-101", "MATH-101"],
            "25C21512": []  # Freshman with no prereqs
        }

    def get_completed_courses(self, enrollment_no: str) -> List[str]:
        return self._transcripts.get(enrollment_no, [])

    def record_completed_course(self, enrollment_no: str, course_code: str):
        if enrollment_no not in self._transcripts:
            self._transcripts[enrollment_no] = []
        if course_code.upper() not in self._transcripts[enrollment_no]:
            self._transcripts[enrollment_no].append(course_code.upper())
