# CivicConnect

CivicConnect is a community issue reporting and tracking application. Citizens can submit local complaints, attach photos, follow status updates, and provide feedback. Administrators can review and prioritize reports, update their status, and monitor overdue work.

## Tech stack

- Backend: Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Frontend: React, Vite, React Router, Tailwind CSS
- Authentication: JWT bearer tokens with bcrypt password hashing, plus Firebase Google and phone sign-in
- Tests: pytest

## Project structure

```text
app/                 FastAPI routes, database models, auth, and services
migrations/          Alembic migration environment and revisions
scripts/             Administrative and maintenance scripts
tests/               Backend pytest suite
frontend/             React application and Vite configuration
uploads/              Uploaded complaint images (ignored by Git)
.env.example          Example backend configuration
requirements.txt      Python dependencies
alembic.ini           Alembic configuration
```

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer and npm
- PostgreSQL 14 or newer

## Setup and run

1. Create a PostgreSQL database and user for the application. For example, from `psql` as a PostgreSQL administrator:

   ```sql
   CREATE USER civicconnect WITH PASSWORD 'choose-a-local-password';
   CREATE DATABASE civicconnect OWNER civicconnect;
   ```

2. Copy `.env.example` to `.env` in the project root. Set `DATABASE_URL` to your PostgreSQL connection string and replace `JWT_SECRET_KEY` with a long, random secret. Keep `.env` private.
3. Create and activate a Python virtual environment from the project root:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS or Linux, activate with `source .venv/bin/activate`.
4. Install the Python dependencies:

   ```sh
   pip install -r requirements.txt
   ```
5. Apply the database migrations:

   ```sh
   alembic upgrade head
   ```
6. Create an administrator account. Supply your own name, email, and password; do not put a real password in shared documentation or shell history:

   ```sh
   python scripts/create_admin.py --name "Admin Name" --email admin@example.com --password "your-local-password"
   ```
7. Start the API from the project root:

   ```sh
   uvicorn app.main:app --reload
   ```

   The API documentation is available at `http://localhost:8000/docs`.
8. In another terminal, install and run the frontend:

   ```sh
   cd frontend
   cp .env.example .env
   npm install
   npm run dev
   ```

   Open the Vite URL shown in the terminal, usually `http://localhost:5173`.

### Google and phone sign-in setup

Google and SMS sign-in use Firebase Authentication. Create a Firebase project and web app, enable the Google and Phone providers under Authentication, and add your local frontend domain (`localhost` and `127.0.0.1`) and deployed domain to the authorized domains list. Copy the web app's API key, auth domain, project ID, and app ID into `frontend/.env`. The backend also needs `FIREBASE_PROJECT_ID` and Firebase Admin credentials. For local use, download a service account JSON outside the repository, set `GOOGLE_APPLICATION_CREDENTIALS` to its path in the root `.env`, and keep that key private. For a hosted backend, set `FIREBASE_SERVICE_ACCOUNT_JSON` as a private environment variable. Firebase Phone Authentication uses SMS verification and requires a billing account for production use; charges are per sent SMS. After filling the settings, restart both servers. See [Firebase Google sign-in](https://firebase.google.com/docs/auth/web/google-signin), [Firebase phone sign-in](https://firebase.google.com/docs/auth/web/phone-auth), and [Firebase ID-token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens).

## Deploying

You can deploy the React frontend to Vercel from this repository by creating a Vercel project with `frontend` as its Root Directory. Use `npm run build` as the build command and `dist` as the output directory. Set `VITE_API_URL` to the public URL of the deployed API and set `VITE_FIREBASE_API_KEY`, `VITE_FIREBASE_AUTH_DOMAIN`, `VITE_FIREBASE_PROJECT_ID`, and `VITE_FIREBASE_APP_ID` in the Vercel project's Environment Variables. These `VITE_` values are included in the public browser bundle, so never put server secrets in them.

The API needs a separately reachable PostgreSQL database. Set `DATABASE_URL`, `JWT_SECRET_KEY`, `FIREBASE_PROJECT_ID`, `FIREBASE_SERVICE_ACCOUNT_JSON`, and `CORS_ALLOWED_ORIGINS` on the API host, allowing the deployed frontend origin in CORS and Firebase Authentication's authorized domains. Apply `alembic upgrade head` to that database and create the production admin account against it. The admin dashboard will show production data because it reads from the same API and database.

Vercel can run FastAPI, but this app currently writes complaint photos to local `uploads/` and starts an in-process scheduler. Vercel Functions have a read-only filesystem except for temporary `/tmp` storage, so uploaded photos need persistent object storage. The scheduler also needs a continuously running worker or an external scheduled job. Until those pieces are adapted, use Vercel for the frontend and a host that supports persistent file storage/background jobs for the API. Also check Vercel's current Hobby terms: its free plan is limited to personal and non-commercial use. See [Vercel's FastAPI guide](https://vercel.com/docs/frameworks/backend/fastapi), [Vercel function runtimes](https://vercel.com/docs/functions/runtimes), and [Hobby plan terms](https://vercel.com/docs/plans/hobby).

## Tests

Run backend tests from the project root with the virtual environment active:

```sh
pytest
```

## Algorithms

**Complaint categorization** respects a category selected by the citizen. When none is provided, it scans the description case-insensitively for configured keywords covering safety, drainage, sanitation, electricity, roads, and water; unmatched reports are categorized as Other.

**Priority scoring** starts with a severity weight (Low 1, Medium 2, High 3) multiplied by 20, adds 10 points per linked duplicate and 2 points per day pending, then clamps the score to 0–100. Score thresholds map the report to Low, Medium, High, or Critical priority, each with a corresponding service target.

**Duplicate detection** finds the oldest unresolved complaint from the last seven days with the same category and location, compared without case or surrounding whitespace. A match links the new report to the original and increases the original's duplicate count and priority.

**Overdue and aging updates** run every 15 minutes. The scheduler recalculates age-based priority for unresolved complaints and marks reports overdue when their expected resolution time has passed. Administrators can also request an immediate recalculation.

## Main API routes

Authentication: `POST /auth/register`, `POST /auth/login`, `POST /auth/firebase`, `GET /auth/me`.

Complaints: `POST /complaints`, `GET /complaints/my`, `GET /complaints/{complaint_id}`, `GET /complaints/{complaint_id}/timeline`, `POST /complaints/{complaint_id}/photo`, `POST /complaints/{complaint_id}/feedback`.

Administration (admin access): `GET /admin/complaints`, `GET /admin/queue`, `GET /admin/overdue`, `GET /admin/stats`, `PATCH /admin/complaints/{complaint_id}/status`, `POST /admin/complaints/{complaint_id}/after-photo`, `POST /admin/recalculate`.

Notifications: `GET /notifications`, `PATCH /notifications/{notification_id}/read`, `PATCH /notifications/read-all`.

Service status: `GET /health`. Uploaded images are served from `/uploads/{filename}`.
