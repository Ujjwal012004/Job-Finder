# Job Finder

A full-stack application to search, save, track, and manage job applications.

## Tech Stack

| Layer      | Technology                  |
|------------|-----------------------------|
| Backend    | Python / FastAPI             |
| Database   | PostgreSQL (SQLite for dev)  |
| ORM        | SQLAlchemy 2.0               |
| Frontend   | React + Vite (vanilla CSS)   |

## Project Structure

```
Job Finder/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic Settings (env-based config)
│   │   ├── database.py         # Engine, session factory, Base
│   │   └── models/
│   │       ├── __init__.py
│   │       ├── user.py
│   │       ├── company.py
│   │       ├── job.py
│   │       ├── application.py
│   │       ├── saved_job.py
│   │       └── application_note.py
│   ├── requirements.txt
│   └── schema.sql              # Raw DDL for review
├── frontend/                   # (Phase 5)
├── .gitignore
└── README.md
```

## Setup (Development)

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

## Database Schema

Six normalized tables: `users`, `companies`, `jobs`, `applications`, `saved_jobs`, `application_notes`.

See `backend/schema.sql` for the full DDL.

## Development Phases

- [x] Phase 1: Architecture & Data Layer
- [ ] Phase 2: Core Backend Logic
- [ ] Phase 3: Specialized Service
- [ ] Phase 4: API Integration & Testing
- [ ] Phase 5: Presentation Layer (Frontend)
