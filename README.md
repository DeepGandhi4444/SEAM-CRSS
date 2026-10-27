# Course Registration and Scheduling System (CRSS)

**Author:** Deep C. Gandhi  
**Enrollment Number:** 25C21510  
**Subject:** Software Engineering & Agile Methodology (SEAM)  
**Program:** Third Year — B.E. / B.Tech (Computer Science & Engineering / IT) — Class 01 Batch 2024–28  
**Institution:** ITM SLS Baroda University, School of Computer Science Engineering and Technology  
**GitHub Repository:** [https://github.com/DeepGandhi4444/SEAM-CRSS](https://github.com/DeepGandhi4444/SEAM-CRSS)  
**Agile Scrum Board:** [https://github.com/DeepGandhi4444/SEAM-CRSS/milestone/1](https://github.com/DeepGandhi4444/SEAM-CRSS/milestone/1)  

---

## 1. Project Overview

The **Course Registration and Scheduling System (CRSS)** is an enterprise-grade academic web application designed to automate and streamline the student registration lifecycle. The project replaces error-prone, manual paper-based processes with an atomic, transactional system that prevents overbooking, detects schedule conflicts in real time, enforces academic prerequisites, and manages tuition billing.

This project represents the complete, unified implementation of the software engineering and agile practices developed across **Practicals 3 through 8** of the SEAM Laboratory Manual.

---

## 2. Key Features & Architectural Modules

The codebase is organized into a modular, decoupled Python package (`crss/`):

1. **Authentication & Session Security (`crss/auth.py` — Practical 6):**
   * **Dual-Mode Authentication:** Synthesizes campus OAuth2 Single Sign-On (SSO) with local RSA256/HMAC-SHA256 JSON Web Tokens (JWT).
   * Cryptographic signature verification and token tamper detection.

2. **Domain Object Model (`crss/models.py` — Practical 3):**
   * Object-oriented domain hierarchy implementing the Practical 3 UML Class Diagram:
     * Abstract `User` base class with `Student`, `Faculty`, and `Administrator` specializations.
     * `Course` and `CourseSection` entities with atomic seat tracking.
     * `TimeSlot` with temporal overlap detection algorithms (supporting zero-gap back-to-back classes).
     * `Timetable` schedule grid preventing double-booking.

3. **Registration Engine & Cart (`crss/registration.py` — Practical 7 & Practical 3–5):**
   * **Course Registration Cart:** Developed via Test-Driven Development (TDD) Red-Green-Refactor cycles.
   * **Constraint Enforcement:** Enforces maximum 18-credit overload limits and blocks duplicate course enrollments.
   * **Prerequisite Verification Engine:** Automatically inspects student transcripts via the Student Information Database (SIS) service.
   * **Real-Time Clash Detection:** Evaluates temporal overlap against already enrolled courses.
   * **Pricing Strategy Pattern:** Open/Closed Principle implementation supporting merit scholarships and fee waivers.

4. **Student Financial Ledger & Billing (`crss/billing.py` — Practical 8):**
   * Manages student balances, tuition debits, refunds, and administrative financial holds.
   * Designed with dependency injection for clean mock testing.

5. **Supporting Gateways & Services (`crss/services.py`):**
   * `NotificationService`: Asynchronous email, SMS, and in-app receipt dispatcher.
   * `AuditLoggerService`: Immutable transaction log for compliance and auditing.
   * `StudentInfoDatabaseService`: University SIS interface.

---

## 3. Directory Structure

```
CRSS/
│
├── README.md                          # Comprehensive project documentation & run guide
├── requirements.txt                   # Project dependencies and testing frameworks
├── main.py                            # Interactive end-to-end CLI demonstration script
│
├── crss/                              # Core application package
│   ├── __init__.py                    # Package initializer & version metadata
│   ├── models.py                      # Domain entities (User, Student, Course, Section, Timetable)
│   ├── auth.py                        # SSO & JWT authentication engine
│   ├── registration.py                # Cart, prerequisite engine, clash detector & registration
│   ├── billing.py                     # StudentFeeAccount & tuition transactions
│   ├── services.py                    # External services (Notification, SIS, Audit Logger)
│   └── exceptions.py                  # Custom domain exception hierarchy
│
└── tests/                             # Comprehensive automated test suite
    ├── __init__.py                    # Test package marker
    ├── conftest.py                    # Pytest shared fixtures and mock doubles
    ├── test_auth.py                   # Authentication & token verification tests
    ├── test_registration.py           # TDD cart, clash detection & prerequisite tests
    └── test_billing.py                # Boundary Value Analysis (BVA), EP & mock tests
```

---

## 4. Prerequisites & System Requirements

Before running the project, ensure your workstation meets the following requirements:

* **Operating System:** Windows 10/11, macOS, or Linux.
* **Python Runtime:** **Python 3.8 or higher** (Python 3.10 / 3.11 / 3.12 recommended).
  * Check your Python version by opening a terminal and running:
    ```bash
    python --version
    ```
* **Package Manager:** `pip` (standard with Python).

---

## 5. Installation & Setup Instructions

Follow these step-by-step instructions to set up the environment:

### Step 1: Open Terminal in Project Directory
Navigate to the `CRSS` folder:
```bash
cd "d:\college files\PRACTICALS\SEAM\CRSS"
```

### Step 2: (Recommended) Create and Activate a Virtual Environment
Using a virtual environment isolates project dependencies:

* **On Windows (PowerShell / Command Prompt):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

* **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 3: Install Required Dependencies
Install the required testing frameworks and utilities:
```bash
pip install -r requirements.txt
```

---

## 6. How to Run the Application

Execute the main interactive demonstration script:

```bash
python main.py
```

### What `main.py` Demonstrates:
1. **Student SSO Authentication:** Authenticates student `25C21510` and issues a session token.
2. **Catalog Browsing:** Displays live course section offerings, meeting timeslots, and available seats.
3. **Happy Path Registration:** Atomically enrolls the student into `CS-301-A` and `CS-310-A`, decrementing seats and updating the timetable.
4. **Schedule Conflict Prevention:** Attempts to register for a conflicting section (`MATH-220-A`), demonstrating immediate detection and rollback.
5. **Prerequisite Enforcement:** Demonstrates a freshman student being blocked from enrolling in an advanced course without completing prerequisites.
6. **Timetable Visualization:** Renders the student's personalized weekly schedule.
7. **Tuition Billing & Scholarships:** Calculates tuition with a 10% Merit Scholarship fee waiver and debits the student ledger.
8. **Asynchronous Notification Log:** Displays sent email confirmations and audit log events.

---

## 7. How to Run the Automated Test Suite

The project includes a comprehensive suite of unit tests, BDD scenarios, boundary value tests, and mock verifications.

### Run All Unit Tests
From the `CRSS` directory, execute:
```bash
pytest -v
```

### Run Tests with Code Coverage Report
To view statement and branch coverage metrics (targeting > 95% coverage):
```bash
pytest --cov=crss --cov-report=term-missing
```

### Run Specific Test Modules
* **Test Authentication Module:**
  ```bash
  pytest tests/test_auth.py -v
  ```
* **Test Registration Cart & Workflows (Practical 7 TDD Cycles):**
  ```bash
  pytest tests/test_registration.py -v
  ```
* **Test Fee Account, BVA & Mocks (Practical 8):**
  ```bash
  pytest tests/test_billing.py -v
  ```

---

## 8. Mapping to Lab Manual Practicals

| Practical No. | Topic in Lab Manual | Implementation in `CRSS` Codebase |
| :--- | :--- | :--- |
| **Practical 3** | UML Use Case & Class Diagram Design | [`crss/models.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/crss/models.py) implements the complete domain model with inheritance and multiplicity constraints. |
| **Practical 4** | Scrum Project Backlog to Sprint Backlog | [`main.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/main.py) and [`crss/registration.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/crss/registration.py) execute the committed Sprint 1 MVP registration stories. |
| **Practical 5** | Writing User Stories (INVEST & BDD) | [`tests/test_registration.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/tests/test_registration.py) automates the Given-When-Then acceptance criteria for US-04, US-05, and US-06. |
| **Practical 6** | Version Control (Git & GitHub) | [`crss/auth.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/crss/auth.py) features the unified authentication handler resolving the feature branch conflict. |
| **Practical 7** | Test-Driven Development (TDD) | [`crss/registration.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/crss/registration.py) (`CourseCart`) and [`tests/test_registration.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/tests/test_registration.py) implement all 6 TDD cycles. |
| **Practical 8** | Unit Testing & Test Automation | [`crss/billing.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/crss/billing.py) and [`tests/test_billing.py`](file:///d:/college%20files/PRACTICALS/SEAM/CRSS/tests/test_billing.py) provide 14 BVA, Equivalence Partitioning, and Mock tests. |

---

*Project authored by Deep C. Gandhi (Enrollment: 25C21510) for ITM SLS Baroda University.*
