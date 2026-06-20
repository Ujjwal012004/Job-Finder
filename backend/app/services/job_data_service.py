"""
Job Data Service — Import, seed, and manage job data.

This service handles the data ingestion pipeline:
    - Seeding the database with sample data for development
    - Importing jobs from external sources (simulated)
    - Data validation and deduplication before insertion

OOP Concepts Demonstrated:
    1. **Template Method Pattern**: The `import_jobs()` method defines
       the import algorithm skeleton (validate → deduplicate → insert),
       and each step can be overridden by subclasses for different
       data sources.
    2. **Factory Method (implicit)**: `_create_job_from_raw()` acts as
       a factory that transforms raw dictionaries into validated ORM
       objects, encapsulating the creation logic.
    3. **Defensive Programming**: Every public method validates its
       inputs and returns structured results (not raw exceptions).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.company import Company
from app.models.job import Job

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """Summary of a data import operation."""
    total_processed: int = 0
    created: int = 0
    skipped_duplicate: int = 0
    skipped_invalid: int = 0
    errors: List[str] = field(default_factory=list)


# ── Validation Constants ─────────────────────────────────────────
VALID_EMPLOYMENT_TYPES = {"full-time", "part-time", "contract", "internship", "freelance"}
VALID_EXPERIENCE_LEVELS = {"entry", "mid", "senior", "lead", "executive"}
VALID_JOB_STATUSES = {"active", "closed", "expired"}


class JobDataService:
    """
    Handles job data import, seeding, and validation.

    This service is completely decoupled from HTTP — it can be called
    from API routes, CLI scripts, background workers, or test suites.
    """

    def __init__(self, db: Session):
        self._db = db

    # ── Public API ───────────────────────────────────────────────

    def import_jobs(self, raw_jobs: List[Dict[str, Any]]) -> ImportResult:
        """
        Import a batch of jobs from raw dictionaries.

        Pipeline steps:
            1. Validate each raw job dict
            2. Resolve or create the company
            3. Check for duplicates (same title + company)
            4. Insert new jobs

        This is the Template Method pattern — the overall algorithm
        is fixed, but individual steps can be customized.
        """
        result = ImportResult(total_processed=len(raw_jobs))

        for i, raw in enumerate(raw_jobs):
            try:
                # Step 1: Validate
                validation_error = self._validate_raw_job(raw)
                if validation_error:
                    result.skipped_invalid += 1
                    result.errors.append(f"Job #{i + 1}: {validation_error}")
                    continue

                # Step 2: Resolve company
                company = self._resolve_company(raw.get("company_name", "Unknown"))

                # Step 3: Check for duplicates
                if self._is_duplicate(raw["title"], company.id):
                    result.skipped_duplicate += 1
                    continue

                # Step 4: Create job
                self._create_job_from_raw(raw, company.id)
                result.created += 1

            except Exception as e:
                result.errors.append(f"Job #{i + 1}: Unexpected error — {str(e)}")
                logger.error(f"Import error for job #{i + 1}: {e}", exc_info=True)

        return result

    def seed_sample_data(self) -> ImportResult:
        """
        Seed the database with realistic sample job data.

        Useful for:
            - Development environment setup
            - Demo deployments
            - Testing the frontend with real-looking data
        """
        sample_jobs = [
            {
                "company_name": "TechNova Labs",
                "company_website": "https://technovalabs.io",
                "company_industry": "Technology",
                "title": "Senior Full-Stack Developer",
                "description": "Build and maintain scalable web applications using React, Node.js, and PostgreSQL. Lead technical design reviews and mentor junior developers.",
                "location": "San Francisco, CA",
                "employment_type": "full-time",
                "experience_level": "senior",
                "salary_min": 150000,
                "salary_max": 200000,
                "is_remote": True,
                "source": "seed",
            },
            {
                "company_name": "DataStream AI",
                "company_website": "https://datastream.ai",
                "company_industry": "Artificial Intelligence",
                "title": "Machine Learning Engineer",
                "description": "Design and deploy ML models for real-time data processing. Experience with PyTorch, TensorFlow, and MLOps pipelines required.",
                "location": "New York, NY",
                "employment_type": "full-time",
                "experience_level": "mid",
                "salary_min": 130000,
                "salary_max": 175000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "CloudScale Systems",
                "company_website": "https://cloudscale.dev",
                "company_industry": "Cloud Computing",
                "title": "DevOps Engineer",
                "description": "Manage Kubernetes clusters, CI/CD pipelines, and cloud infrastructure on AWS/GCP. Terraform and Ansible experience preferred.",
                "location": "Austin, TX",
                "employment_type": "full-time",
                "experience_level": "mid",
                "salary_min": 120000,
                "salary_max": 160000,
                "is_remote": True,
                "source": "seed",
            },
            {
                "company_name": "FinEdge Capital",
                "company_website": "https://finedge.com",
                "company_industry": "Finance",
                "title": "Backend Developer (Python)",
                "description": "Build high-performance trading systems and APIs. Strong knowledge of Python, FastAPI, and financial protocols required.",
                "location": "Chicago, IL",
                "employment_type": "full-time",
                "experience_level": "senior",
                "salary_min": 160000,
                "salary_max": 220000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "GreenByte Studio",
                "company_website": "https://greenbyte.studio",
                "company_industry": "Gaming",
                "title": "Unity Game Developer",
                "description": "Create immersive 3D experiences using Unity and C#. Work with artists and designers to bring game concepts to life.",
                "location": "Los Angeles, CA",
                "employment_type": "full-time",
                "experience_level": "mid",
                "salary_min": 100000,
                "salary_max": 140000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "TechNova Labs",
                "company_website": "https://technovalabs.io",
                "company_industry": "Technology",
                "title": "Frontend Developer (React)",
                "description": "Create pixel-perfect UI components with React, TypeScript, and modern CSS. Collaborate with the design team on a component library.",
                "location": "Remote",
                "employment_type": "full-time",
                "experience_level": "entry",
                "salary_min": 80000,
                "salary_max": 110000,
                "is_remote": True,
                "source": "seed",
            },
            {
                "company_name": "DataStream AI",
                "company_website": "https://datastream.ai",
                "company_industry": "Artificial Intelligence",
                "title": "Data Engineering Intern",
                "description": "Assist in building ETL pipelines and data warehouses. Learn Apache Spark, Airflow, and cloud data platforms.",
                "location": "New York, NY",
                "employment_type": "internship",
                "experience_level": "entry",
                "salary_min": 30000,
                "salary_max": 50000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "SecureNet Corp",
                "company_website": "https://securenet.io",
                "company_industry": "Cybersecurity",
                "title": "Cybersecurity Analyst",
                "description": "Monitor security systems, investigate incidents, and implement security controls. CISSP or CEH certification preferred.",
                "location": "Washington, DC",
                "employment_type": "full-time",
                "experience_level": "mid",
                "salary_min": 110000,
                "salary_max": 145000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "CloudScale Systems",
                "company_website": "https://cloudscale.dev",
                "company_industry": "Cloud Computing",
                "title": "Site Reliability Engineer",
                "description": "Ensure 99.99% uptime for distributed systems. Deep knowledge of monitoring, alerting, and incident response required.",
                "location": "Seattle, WA",
                "employment_type": "full-time",
                "experience_level": "senior",
                "salary_min": 155000,
                "salary_max": 200000,
                "is_remote": True,
                "source": "seed",
            },
            {
                "company_name": "PixelCraft Design",
                "company_website": "https://pixelcraft.design",
                "company_industry": "Design",
                "title": "UI/UX Designer",
                "description": "Design intuitive user interfaces for web and mobile applications. Proficiency in Figma, user research, and prototyping required.",
                "location": "Portland, OR",
                "employment_type": "contract",
                "experience_level": "mid",
                "salary_min": 90000,
                "salary_max": 130000,
                "is_remote": True,
                "source": "seed",
            },
            {
                "company_name": "HealthTech Solutions",
                "company_website": "https://healthtech.solutions",
                "company_industry": "Healthcare",
                "title": "Software Engineer (Java)",
                "description": "Develop HIPAA-compliant healthcare applications using Java Spring Boot and microservices architecture.",
                "location": "Boston, MA",
                "employment_type": "full-time",
                "experience_level": "mid",
                "salary_min": 115000,
                "salary_max": 155000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "RoboFlow Dynamics",
                "company_website": "https://roboflow.tech",
                "company_industry": "Robotics",
                "title": "Embedded Systems Engineer",
                "description": "Program microcontrollers and design firmware for autonomous robot platforms. C/C++ and RTOS experience required.",
                "location": "Denver, CO",
                "employment_type": "full-time",
                "experience_level": "senior",
                "salary_min": 140000,
                "salary_max": 185000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "EcoVenture",
                "company_website": "https://ecoventure.org",
                "company_industry": "Sustainability",
                "title": "Part-Time Data Analyst",
                "description": "Analyze environmental datasets and create dashboards using Python, Pandas, and Tableau. Flexible hours.",
                "location": "Remote",
                "employment_type": "part-time",
                "experience_level": "entry",
                "salary_min": 35000,
                "salary_max": 55000,
                "is_remote": True,
                "source": "seed",
            },
            {
                "company_name": "FinEdge Capital",
                "company_website": "https://finedge.com",
                "company_industry": "Finance",
                "title": "Quantitative Developer",
                "description": "Build pricing models and risk analytics engines. Strong math background with Python/C++ proficiency required.",
                "location": "New York, NY",
                "employment_type": "full-time",
                "experience_level": "lead",
                "salary_min": 200000,
                "salary_max": 300000,
                "is_remote": False,
                "source": "seed",
            },
            {
                "company_name": "GreenByte Studio",
                "company_website": "https://greenbyte.studio",
                "company_industry": "Gaming",
                "title": "Freelance 3D Artist",
                "description": "Create high-quality 3D models and textures for upcoming game titles. Blender and Substance Painter expertise needed.",
                "location": "Remote",
                "employment_type": "freelance",
                "experience_level": "mid",
                "salary_min": 60000,
                "salary_max": 100000,
                "is_remote": True,
                "source": "seed",
            },
        ]

        return self.import_jobs(sample_jobs)

    # ── Private Helpers ──────────────────────────────────────────

    def _validate_raw_job(self, raw: Dict[str, Any]) -> Optional[str]:
        """
        Validate a raw job dictionary.

        Returns None if valid, or an error message string if invalid.
        This is defensive programming — we never trust external data.
        """
        if not raw.get("title"):
            return "Missing required field: title"
        if not raw.get("company_name"):
            return "Missing required field: company_name"

        emp_type = raw.get("employment_type", "full-time")
        if emp_type not in VALID_EMPLOYMENT_TYPES:
            return f"Invalid employment_type: '{emp_type}'"

        exp_level = raw.get("experience_level")
        if exp_level and exp_level not in VALID_EXPERIENCE_LEVELS:
            return f"Invalid experience_level: '{exp_level}'"

        salary_min = raw.get("salary_min")
        salary_max = raw.get("salary_max")
        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                return f"salary_min ({salary_min}) > salary_max ({salary_max})"

        return None  # Valid

    def _resolve_company(self, company_name: str, **kwargs) -> Company:
        """
        Find an existing company by name, or create a new one.

        This is an upsert pattern — "get or create".  It ensures
        we don't create duplicate company records.
        """
        company = (
            self._db.query(Company)
            .filter(Company.name == company_name)
            .first()
        )

        if company:
            return company

        # Create new company
        company = Company(
            name=company_name,
            website=kwargs.get("company_website"),
            industry=kwargs.get("company_industry"),
        )
        self._db.add(company)
        self._db.flush()  # Get the ID without committing
        return company

    def _is_duplicate(self, title: str, company_id: int) -> bool:
        """Check if a job with the same title already exists for this company."""
        return (
            self._db.query(Job)
            .filter(Job.title == title, Job.company_id == company_id)
            .first()
        ) is not None

    def _create_job_from_raw(self, raw: Dict[str, Any], company_id: int) -> Job:
        """
        Factory method: transforms a raw dictionary into a Job ORM object.

        This encapsulates the mapping logic so callers don't need to
        know which dict keys map to which model attributes.
        """
        job = Job(
            company_id=company_id,
            title=raw["title"],
            description=raw.get("description"),
            location=raw.get("location"),
            employment_type=raw.get("employment_type", "full-time"),
            experience_level=raw.get("experience_level"),
            salary_min=raw.get("salary_min"),
            salary_max=raw.get("salary_max"),
            salary_currency=raw.get("salary_currency", "USD"),
            source=raw.get("source"),
            source_url=raw.get("source_url"),
            is_remote=raw.get("is_remote", False),
            status=raw.get("status", "active"),
            posted_at=raw.get("posted_at", datetime.now(timezone.utc)),
        )
        self._db.add(job)
        self._db.commit()
        return job
