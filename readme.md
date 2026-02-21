# MindSettler Backend

Backend service for **MindSettler**, a mental wellness counseling session booking platform developed during **GWOC (Google Winter of Code)** under **DSC Surat**.

This repository contains the workflow-driven Django REST backend responsible for consultation booking lifecycle management, approvals, scheduling, and secure data handling.

🔗 Full collaborative MindSettler platform: https://github.com/ShreyaSVNIT/mindsettler

> I contributed as the backend developer, designing the session state machine, approval logic, and data architecture powering the platform.

---

---

## Overview

The MindSettler backend powers the complete lifecycle of a consultation booking:

- Draft booking creation
- Email verification
- Admin approval & slot assignment
- Payment initiation & confirmation
- Cancellation with verification
- Public booking status tracking
- Admin-side booking creation & calendar management

The architecture is API-first and state-machine driven, with strong validation and strict lifecycle enforcement.

---

## Tech Stack

- **Backend Framework**: Django
- **API Framework**: Django REST Framework (DRF)
- **Database**: PostgreSQL (production), SQLite (zero-setup local fallback)
- **Authentication**: Token-based (API-first)
- **Email**: Transactional email (verification, confirmations)
- **Admin UI**: Django Admin + Jazzmin
- **Deployment**: Non-Docker (standard Django service)

> PostgreSQL is used in production deployments. For local development and evaluation, the backend automatically falls back to SQLite if no `DATABASE_URL` is provided, allowing the project to run without external database setup.

---

## Core Features

### 1. Booking Lifecycle (Fully Implemented)

Bookings move through a **strict state machine**:

```
DRAFT → PENDING → APPROVED → PAYMENT_PENDING → CONFIRMED → COMPLETED
                         ↘
                          CANCELLED / REJECTED
```

Invalid state transitions are explicitly blocked at the backend level.

---

### 2. Email Verification System

Email verification is mandatory for:
- Booking confirmation
- Payment initiation
- Cancellation confirmation
- Booking detail access

All verification actions are token-based and time-safe.

---

### 3. Public APIs (Frontend-Focused)

The backend exposes REST APIs designed for direct frontend consumption:

- Create booking draft
- Verify email
- Check booking status (via acknowledgement ID or email)
- Initiate & complete payment
- Request & verify cancellation

CSRF is intentionally disabled since this is a **pure API backend**.

---

### 4. Admin Capabilities

Admins can:
- View bookings in **calendar and list views**
- Approve / reject bookings
- Assign time slots
- Create bookings manually from admin
- Track booking states visually
- Filter bookings by status and date

Admin-created bookings:
- Automatically generate acknowledgement IDs
- Follow the same state machine as user bookings
- Bypass email verification where appropriate

---

### 5. Acknowledgement ID System

Every booking is assigned a unique, human-readable acknowledgement ID:

```
MS-XXXXXX
```

This ID is used for:
- Public status tracking
- Payment flows
- Support references
- Email communication

---

### 6. Validation & Safety Guarantees

The backend enforces:
- One active booking per user (email-based)
- Email verification before sensitive actions
- Payment-before-confirmation
- No silent failures (all invalid actions return explicit errors)

All business rules are enforced server-side.

---

## System Relationship

MindSettler consists of multiple services:

- Frontend client  
- NLP chatbot service  
- Backend booking system (**this repo**)  

The chatbot consumes backend APIs and does not replicate booking logic.

---

> The chatbot is a **separate service** and integrates only via APIs.

---

## Project Structure (Simplified)

```
mindsettler-backend/
├── apps/
│   ├── bookings/
│   ├── users/
│   └── consultants/
├── mindsettler/
│   ├── settings/
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

---

## Security & CORS

- **CORS**: Enabled for trusted frontend origins
- **CSRF**: Disabled (API-only backend)
- **Auth**: Token-based
- **Emails**: Verified before all sensitive operations

---

## Environment Configuration

Required environment variables (production – PostgreSQL):

```
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_URL
EMAIL_HOST
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
FRONTEND_URL
```

### Local Development (No PostgreSQL Required)

If `DATABASE_URL` is not set, the backend automatically uses a local SQLite database:

```
python manage.py migrate
python manage.py runserver
```

This ensures the project remains runnable even if the hosted PostgreSQL instance expires.

---

## Development Status

✅ Booking system fully functional  
✅ Email verification flows stable  
✅ Admin calendar & list views implemented  
✅ Frontend integration tested  
🟢 Production-ready backend  

---

## Notes for Developers

- Do not hardcode frontend flows — rely on API responses
- Treat booking status as the single source of truth
- Avoid bypassing state transitions
- Chatbot should only **consume APIs**, never replicate logic

---

## Author

**Kavya Bhatiya**  
Backend Developer — MindSettler (GWOC, DSC Surat)

---

## License

Internal project — all rights reserved.

---

**MindSettler Backend**  
Built for reliability, clarity, and long-term scalability.