# NEXUS_JOBS: Job Finder Platform

A highly interactive, full-stack job search and application tracking platform featuring a futuristic Cyberpunk UI. Built using a strict phased approach with clear separation of concerns (Facade patterns, Object-Oriented Repositories, layered routing).

## 🚀 Tech Stack

- **Backend**: Python 3, FastAPI, SQLAlchemy, SQLite
- **Frontend**: React 18, Vite, Tailwind CSS v3
- **Authentication**: JWT (JSON Web Tokens) with OAuth2 Password Flow
- **Testing**: Pytest for End-to-End API testing

## 🛠 Project Architecture

The backend strictly follows a layered Object-Oriented Architecture:
1. **API Routes (`/app/routes`)**: Thin HTTP handlers.
2. **Services (`/app/services`)**: Core business logic implementing the Facade pattern.
3. **Repositories (`/app/repositories`)**: Data access layer abstracts away SQLAlchemy ORM queries.
4. **Models & Schemas (`/app/models`, `/app/schemas`)**: Database tables and Pydantic validation schemas.

The frontend is a Component-based React SPA utilizing `AuthContext` for global state management and an Axios interceptor for secure API communication.

## ⚙️ Local Setup

### 1. Start the Backend
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install httpx pytest python-jose[cryptography]

# Start the FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```
> The API will run at `http://localhost:8000/api`
> View automatic Swagger documentation at `http://localhost:8000/docs`

### 2. Seed Mock Data
To populate the database with initial jobs and companies, run the following command (or visit the `/docs` page to execute it):
```bash
curl -X POST "http://localhost:8000/api/seed/jobs"
```

### 3. Start the Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
> The UI will run at `http://localhost:5173`

## 🧠 Utilizing for Real-World Jobs

To transition this platform from mock data to real-world utility:
1. **Personal Tracker**: Use the UI to manually track job applications you make externally (e.g., LinkedIn, Indeed).
2. **API Ingestion**: Create a Python CRON script to pull live data from free job aggregators (like the Adzuna API) and insert it into the SQLite `jobs` table using the `JobDataService`.
3. **Scraping**: Implement BeautifulSoup/Selenium scripts to extract custom job listings from specific company career pages and post them to the database.

## 📜 License
MIT License
