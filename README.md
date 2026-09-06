# Hospital Management System

A full-stack hospital management application supporting three roles — **Admin**, **Doctor**, and **Patient** — with appointment booking, treatment history, scheduled notifications, and async CSV exports.

---

## Tech Stack

**Frontend:** Vue.js 3 (Composition API) + Vite, Vue Router, Axios, Bootstrap, Bootstrap Icons

**Backend:** Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Caching, Flask-CORS, Celery, Redis, SQLite

**Background jobs:** Celery (worker + beat) with Redis as broker/result backend

**Email (dev):** MailHog (catches outgoing mail locally, no real SMTP needed)

---

## Prerequisites

- Python 3.9+ (a virtual environment is recommended, created inside `backend/`)
- Node.js + npm
- Redis server (system-level service — not a Python package)
- MailHog (for catching monthly report emails locally)

---

## Backend Setup

1. Create and activate a virtual environment inside `backend/`:

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. Install dependencies from `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

3. Install and start Redis (system service, separate from the Python `redis` package):

   - **Mac:** `brew install redis` → `brew services start redis` (or run `redis-server` directly)
   - **Ubuntu/Linux:** `sudo apt install redis-server`
   - **Windows:** use WSL, Docker, or a Windows-compatible fork (e.g. Memurai)

4. Install MailHog (catches emails sent by the monthly report job — no real inbox needed):

   - **Mac:** `brew install mailhog`
   - **Linux:** download the binary from the [MailHog releases page](https://github.com/mailhog/MailHog/releases)
   - Web UI available at `http://localhost:8025` once running

5. Configure secrets in `backend/config.py`:

   - `JWT_SECRET_KEY` — currently hardcoded for local dev use
   - `GOOGLE_CHAT_WEBHOOK` — set this to a real Google Chat webhook URL, or use a local mock (see **Webhook Reminders** below) for testing without a Google Workspace account

---

## Frontend Setup

```bash
cd frontend
npm install
```

This installs everything listed in `package.json` (Vue, Vue Router, Axios, Bootstrap, Bootstrap Icons as runtime dependencies; Vite and the Vue plugin as dev dependencies).

---

## Running the App

Redis must be running before Flask or Celery start, since both connect to it on startup. Recommended order:

| # | Terminal | Command |
|---|----------|---------|
| 1 | Redis | `redis-server` |
| 2 | MailHog | `mailhog` |
| 3 | Celery worker | `cd backend && celery -A app.celery worker --loglevel=info` |
| 4 | Celery beat | `cd backend && celery -A app.celery beat --loglevel=info` |
| 5 | Flask backend | `cd backend && python app.py` |
| 6 | Vite frontend | `cd frontend && npm run dev` |

The frontend runs at `http://localhost:5173` (Vite default) and expects the backend at `http://localhost:5000`.

A default **admin account** is created automatically on first run:
- Email: `admin@gmail.com`
- Password: `admin`

### Webhook Reminders Without Google Workspace

Google Chat webhooks require a Workspace account to set up. For local testing without one, point `GOOGLE_CHAT_WEBHOOK` in `config.py` at either:
- [webhook.site](https://webhook.site) — instant hosted URL that displays incoming requests live, or
- A small local Flask endpoint that just logs the received payload

Either lets you verify the daily reminder job fires with the correct message content, without needing real Google Chat access.

---

## Project Structure

```
hospital-management-app/
├── backend/
│   ├── venv/                  (not tracked)
│   ├── app.py                 # App entrypoint, extensions init, Celery beat schedule
│   ├── config.py              # Config classes (DB, Redis, JWT, mail, webhook)
│   ├── extensions.py          # SQLAlchemy, JWTManager, Cache, Celery instances
│   ├── models.py              # User, DoctorProfile, Appointment, History, etc.
│   ├── routes.py              # All API routes (auth, admin, user blueprints)
│   ├── tasks.py                # Celery tasks (reminders, reports, CSV export)
│   ├── templates/
│   │   └── monthly_report.html
│   ├── exports/                # Generated CSV exports (auto-created)
│   └── instance/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Admin/
│   │   │   ├── Doctor/
│   │   │   ├── Patient/
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   └── Navbar.vue
│   │   ├── router/index.js
│   │   ├── App.vue
│   │   └── main.js
│   └── index.html
└── README.md
```

---

## Roles & Features

### Admin (Hospital Staff)

- Single pre-existing superuser — created programmatically on first run; no admin registration flow exists.
- Dashboard shows total counts of doctors, patients, and upcoming appointments.
- Add, edit, and remove doctor profiles (name, department, experience, about).
- Edit or remove patient records.
- View and cancel any appointment (upcoming or past).
- Search doctors and patients by name, ID, email, or department.
- Review and act on doctor-submitted profile change requests (accept or reject with a reason, sent via email).
- Set doctor availability on their behalf.

### Doctor

- Dashboard shows upcoming appointments for the week and a list of assigned patients.
- Mark appointments as completed, adding diagnosis, prescription, and notes in the same step.
- Cancel appointments.
- Set personal availability (time slots and patient limits) for the next 7 days.
- View full treatment history for any assigned patient.
- Update previously recorded diagnoses, prescriptions, or notes.
- Request profile changes (e.g. department, experience, about) — routed to admin for approval, since doctors can't edit these directly.

### Patient

- Register and log in.
- View all departments/specializations and browse doctors within each.
- View a doctor's availability for the next 7 days before booking.
- Book an appointment into an open slot; cancel an upcoming appointment.
- Prevented from double-booking the same doctor while an appointment is already active.
- View upcoming appointments and their status (booked, completed, cancelled).
- View full personal treatment history — diagnosis, prescription, notes — per doctor.
- Edit full name directly; other profile fields aren't patient-editable in the current build.
- Export treatment history as a CSV (see **Async CSV Export** below) and manage/download past exports.

---

## Backend Jobs

### 1. Daily Reminders (Scheduled)

Runs every morning via Celery beat (`crontab(hour=6, minute=0)`). Checks for all appointments booked for the current day and sends a reminder message per appointment via a webhook (Google Chat, or a mock endpoint for local testing).

### 2. Monthly Activity Report (Scheduled)

Runs on the 1st of each month via Celery beat. For each doctor, compiles all appointments completed in the previous month — including diagnosis and prescription details — into an HTML report (`monthly_report.html`) and emails it via SMTP (caught locally by MailHog in development).

### 3. CSV Export (User-Triggered Async)

Triggered from the patient's history view. Queues a Celery task that:
- Generates a CSV of the patient's completed appointments with a given doctor (date, time, patient, doctor, diagnosis, prescription, notes)
- Saves it under `backend/exports/`
- Updates a `Download` record's status to `completed` once done, visible on the patient's **Downloads** page for download or deletion

---

## Performance & Caching

- **Flask-Caching with Redis** backs dashboard endpoints (`admin/dashboard`, `doctor/dashboard`, `patient/dashboard`) with a 30-second timeout, reducing repeated DB queries on frequently polled views.
- Per-user cache keys (via `key_prefix`) ensure doctor and patient dashboards don't collide with each other's cached data.
- Cache is explicitly cleared on any state-changing action (booking, cancelling, treatment updates, login) so dashboards never serve stale data after a write.

---

## Other Core Behaviors

- **Double-booking prevention:** a doctor can't be booked twice for the same date/time, and a patient can't hold two simultaneously active bookings with the same doctor.
- **Appointment lifecycle:** `Booked → Completed` (via doctor treatment entry) or `Booked → Cancelled` (by patient, doctor, or admin — tracked via `cancelled_by`).
- **Search:** admin can search doctors/patients by ID, email, name, or department; patients/admin can browse by department/specialization.
- **History retention:** all completed and cancelled appointments are preserved in a dedicated `History` table (separate from live `Appointment` records), so history remains intact even if a `User` is later deleted.
- **Role-based access control:** enforced via JWT identity + role checks on every protected route (`@jwt_required`, plus custom `admin_required` decorator).


