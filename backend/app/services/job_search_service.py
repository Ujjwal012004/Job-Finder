"""
Job Search Service — The core search and discovery engine.

This is the "brain" of Job Finder. It orchestrates queries across
multiple repositories, applies business rules, computes relevance
scores, and returns enriched results.

WHY THIS IS DECOUPLED FROM ROUTES:
    Routes handle HTTP concerns (status codes, headers, auth).
    This service handles BUSINESS concerns (scoring, filtering logic,
    aggregation). You can call this service from:
        - API routes (production)
        - CLI scripts (batch processing)
        - Unit tests (no HTTP server needed)
        - Background workers (scheduled jobs)

OOP Concepts Demonstrated:
    1. **Strategy Pattern (implicit)**: The scoring logic can be
       swapped by overriding `_compute_relevance_score` in a subclass.
    2. **Facade Pattern**: This service provides a simple interface
       (`search`, `get_recommendations`) that hides the complexity
       of multi-repository coordination.
    3. **Single Responsibility**: Each method does ONE thing —
       search, score, aggregate, or recommend.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from dataclasses import dataclass, field

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case

from app.models.job import Job
from app.models.company import Company
from app.models.application import Application
from app.models.saved_job import SavedJob


@dataclass
class SearchResult:
    """
    Enriched search result wrapping a Job with metadata.

    Using a dataclass instead of a dict gives us:
        - Type safety (IDE autocompletion, static analysis)
        - Immutability guarantees
        - Clear documentation of the result shape
    """
    job: Job
    relevance_score: float = 0.0
    is_saved: bool = False
    has_applied: bool = False


@dataclass
class SearchResponse:
    """Paginated search response with metadata."""
    results: List[SearchResult] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 20
    filters_applied: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JobAggregation:
    """Aggregated statistics for the current search/filter context."""
    total_jobs: int = 0
    by_employment_type: Dict[str, int] = field(default_factory=dict)
    by_experience_level: Dict[str, int] = field(default_factory=dict)
    by_location: Dict[str, int] = field(default_factory=dict)
    remote_count: int = 0
    salary_range: Dict[str, Optional[Decimal]] = field(default_factory=dict)


class JobSearchService:
    """
    Orchestrates job search, scoring, and aggregation.

    This class follows the Facade pattern — it provides a unified
    interface to the complex subsystem of repositories, scoring
    algorithms, and aggregation queries.

    Constructor uses Dependency Injection: the DB session is passed
    in, not created internally. This makes the service testable
    without a real database.
    """

    # ── Scoring Weights (tunable) ────────────────────────────────
    KEYWORD_TITLE_WEIGHT = 10.0      # Title match is most valuable
    KEYWORD_DESC_WEIGHT = 3.0        # Description match is less specific
    REMOTE_BONUS = 2.0               # Remote jobs get a small boost
    SALARY_TRANSPARENCY_BONUS = 1.5  # Jobs showing salary are rewarded
    RECENCY_WEIGHT = 5.0             # Newer jobs score higher

    def __init__(self, db: Session):
        """
        Args:
            db: SQLAlchemy session (injected, not owned).
        """
        self._db = db

    # ── Public API ───────────────────────────────────────────────

    def search(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        is_remote: Optional[bool] = None,
        salary_min: Optional[Decimal] = None,
        salary_max: Optional[Decimal] = None,
        company_name: Optional[str] = None,
        status: str = "active",
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
    ) -> SearchResponse:
        """
        Execute a full search with scoring, pagination, and user context.

        This method:
            1. Builds the query with filters (Query Builder pattern)
            2. Counts total results (for pagination metadata)
            3. Fetches the page of results with eager-loaded relations
            4. Computes relevance scores for each result
            5. Enriches results with user context (saved? applied?)
            6. Sorts by relevance score descending

        Args:
            keyword:          Free-text search across title & description.
            location:         Filter by job location (partial match).
            employment_type:  Exact match on type enum.
            experience_level: Exact match on level enum.
            is_remote:        Filter for remote-only jobs.
            salary_min:       Minimum acceptable salary.
            salary_max:       Maximum salary cap.
            company_name:     Filter by company name (partial match).
            status:           Job status filter (default: active).
            page:             1-indexed page number.
            page_size:        Results per page (max 100).
            user_id:          If provided, enriches results with saved/applied flags.

        Returns:
            SearchResponse with scored, enriched, paginated results.
        """
        # Clamp pagination
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        offset = (page - 1) * page_size

        # Build base query
        query = self._build_filter_query(
            keyword=keyword,
            location=location,
            employment_type=employment_type,
            experience_level=experience_level,
            is_remote=is_remote,
            salary_min=salary_min,
            salary_max=salary_max,
            company_name=company_name,
            status=status,
        )

        # Count total (before pagination)
        total_count = query.count()

        # Fetch page with eager-loaded company
        jobs = (
            query
            .options(joinedload(Job.company))
            .order_by(Job.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # Get user context (which jobs are saved/applied)
        saved_job_ids = set()
        applied_job_ids = set()
        if user_id:
            saved_job_ids = self._get_user_saved_job_ids(user_id)
            applied_job_ids = self._get_user_applied_job_ids(user_id)

        # Score and enrich results
        results = []
        for job in jobs:
            score = self._compute_relevance_score(job, keyword)
            results.append(SearchResult(
                job=job,
                relevance_score=round(score, 2),
                is_saved=job.id in saved_job_ids,
                has_applied=job.id in applied_job_ids,
            ))

        # Sort by relevance (highest first)
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        # Build filters metadata
        filters_applied = {
            k: v for k, v in {
                "keyword": keyword,
                "location": location,
                "employment_type": employment_type,
                "experience_level": experience_level,
                "is_remote": is_remote,
                "salary_min": str(salary_min) if salary_min else None,
                "salary_max": str(salary_max) if salary_max else None,
                "company_name": company_name,
            }.items() if v is not None
        }

        return SearchResponse(
            results=results,
            total_count=total_count,
            page=page,
            page_size=page_size,
            filters_applied=filters_applied,
        )

    def get_aggregations(self, status: str = "active") -> JobAggregation:
        """
        Compute aggregate statistics across all jobs.

        Uses SQL aggregation functions (COUNT, MIN, MAX, GROUP BY)
        which are far more efficient than loading all rows into
        Python and computing in-memory.

        Returns:
            JobAggregation with counts by type, level, location, etc.
        """
        base_query = self._db.query(Job).filter(Job.status == status)

        total = base_query.count()

        # Group by employment_type
        type_counts = (
            self._db.query(Job.employment_type, func.count(Job.id))
            .filter(Job.status == status)
            .group_by(Job.employment_type)
            .all()
        )

        # Group by experience_level
        level_counts = (
            self._db.query(Job.experience_level, func.count(Job.id))
            .filter(Job.status == status, Job.experience_level.isnot(None))
            .group_by(Job.experience_level)
            .all()
        )

        # Top locations
        location_counts = (
            self._db.query(Job.location, func.count(Job.id))
            .filter(Job.status == status, Job.location.isnot(None))
            .group_by(Job.location)
            .order_by(func.count(Job.id).desc())
            .limit(10)
            .all()
        )

        # Remote count
        remote_count = base_query.filter(Job.is_remote.is_(True)).count()

        # Salary range
        salary_stats = (
            self._db.query(
                func.min(Job.salary_min),
                func.max(Job.salary_max),
            )
            .filter(Job.status == status, Job.salary_min.isnot(None))
            .first()
        )

        return JobAggregation(
            total_jobs=total,
            by_employment_type=dict(type_counts),
            by_experience_level=dict(level_counts),
            by_location=dict(location_counts),
            remote_count=remote_count,
            salary_range={
                "min": salary_stats[0] if salary_stats else None,
                "max": salary_stats[1] if salary_stats else None,
            },
        )

    def get_recommendations(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[SearchResult]:
        """
        Generate job recommendations for a user based on their
        application history and saved jobs.

        Algorithm:
            1. Find jobs the user has applied to / saved.
            2. Extract common patterns (companies, locations, types).
            3. Find similar jobs they haven't seen yet.
            4. Score by relevance to their profile.

        This is a simplified content-based recommendation engine.
        """
        # Get user's applied and saved job IDs
        applied_job_ids = self._get_user_applied_job_ids(user_id)
        saved_job_ids = self._get_user_saved_job_ids(user_id)
        seen_job_ids = applied_job_ids | saved_job_ids

        if not seen_job_ids:
            # No history — return latest jobs
            latest = (
                self._db.query(Job)
                .options(joinedload(Job.company))
                .filter(Job.status == "active")
                .order_by(Job.created_at.desc())
                .limit(limit)
                .all()
            )
            return [SearchResult(job=j, relevance_score=1.0) for j in latest]

        # Extract profile from seen jobs
        seen_jobs = (
            self._db.query(Job)
            .filter(Job.id.in_(seen_job_ids))
            .all()
        )

        # Collect preferred attributes
        preferred_companies = {j.company_id for j in seen_jobs}
        preferred_locations = {j.location for j in seen_jobs if j.location}
        preferred_types = {j.employment_type for j in seen_jobs}

        # Find candidate jobs (not already seen)
        candidates = (
            self._db.query(Job)
            .options(joinedload(Job.company))
            .filter(
                Job.status == "active",
                Job.id.notin_(seen_job_ids) if seen_job_ids else True,
            )
            .limit(200)  # Cap candidates for performance
            .all()
        )

        # Score candidates based on profile match
        scored = []
        for job in candidates:
            score = 0.0
            if job.company_id in preferred_companies:
                score += 5.0  # Same company
            if job.location in preferred_locations:
                score += 3.0  # Same location
            if job.employment_type in preferred_types:
                score += 2.0  # Same type
            if job.is_remote:
                score += 1.0  # Remote bonus

            scored.append(SearchResult(
                job=job,
                relevance_score=round(score, 2),
                is_saved=job.id in saved_job_ids,
                has_applied=False,  # Excluded by definition
            ))

        # Sort by score and return top N
        scored.sort(key=lambda r: r.relevance_score, reverse=True)
        return scored[:limit]

    # ── Private Helpers ──────────────────────────────────────────

    def _build_filter_query(
        self,
        keyword: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        is_remote: Optional[bool] = None,
        salary_min: Optional[Decimal] = None,
        salary_max: Optional[Decimal] = None,
        company_name: Optional[str] = None,
        status: str = "active",
    ):
        """
        Build a filtered SQLAlchemy query incrementally.

        This is the Query Builder pattern: each filter condition
        is appended only if the corresponding parameter is provided.
        The result is a composable query object (not executed yet).
        """
        query = self._db.query(Job)

        if status:
            query = query.filter(Job.status == status)
        if keyword:
            query = query.filter(
                Job.title.ilike(f"%{keyword}%")
                | Job.description.ilike(f"%{keyword}%")
            )
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if employment_type:
            query = query.filter(Job.employment_type == employment_type)
        if experience_level:
            query = query.filter(Job.experience_level == experience_level)
        if is_remote is not None:
            query = query.filter(Job.is_remote == is_remote)
        if salary_min is not None:
            query = query.filter(Job.salary_max >= salary_min)
        if salary_max is not None:
            query = query.filter(Job.salary_min <= salary_max)
        if company_name:
            query = query.join(Company).filter(Company.name.ilike(f"%{company_name}%"))

        return query

    def _compute_relevance_score(
        self,
        job: Job,
        keyword: Optional[str],
    ) -> float:
        """
        Compute a relevance score for a single job.

        Scoring factors:
            - Keyword match in title (high weight)
            - Keyword match in description (lower weight)
            - Remote availability (small bonus)
            - Salary transparency (small bonus)
            - Recency (newer = higher)

        This method can be overridden in a subclass to implement
        different scoring strategies (Strategy Pattern).
        """
        score = 0.0

        if keyword:
            kw_lower = keyword.lower()
            if job.title and kw_lower in job.title.lower():
                score += self.KEYWORD_TITLE_WEIGHT
            if job.description and kw_lower in job.description.lower():
                score += self.KEYWORD_DESC_WEIGHT

        if job.is_remote:
            score += self.REMOTE_BONUS

        if job.salary_min is not None or job.salary_max is not None:
            score += self.SALARY_TRANSPARENCY_BONUS

        # Recency: jobs from the last 7 days get full bonus, older get less
        if job.created_at:
            from datetime import datetime, timezone
            age_days = (datetime.now(timezone.utc) - job.created_at.replace(tzinfo=timezone.utc)).days
            recency_factor = max(0, 1.0 - (age_days / 30.0))  # Decays over 30 days
            score += self.RECENCY_WEIGHT * recency_factor

        return score

    def _get_user_saved_job_ids(self, user_id: int) -> set:
        """Get the set of job IDs a user has saved."""
        rows = (
            self._db.query(SavedJob.job_id)
            .filter(SavedJob.user_id == user_id)
            .all()
        )
        return {r[0] for r in rows}

    def _get_user_applied_job_ids(self, user_id: int) -> set:
        """Get the set of job IDs a user has applied to."""
        rows = (
            self._db.query(Application.job_id)
            .filter(Application.user_id == user_id)
            .all()
        )
        return {r[0] for r in rows}
