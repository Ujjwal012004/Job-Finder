"""
Application Tracker Service — Analytics and insights for job applications.

This service answers questions like:
    - "What's my application success rate?"
    - "How long does each stage take on average?"
    - "Which companies am I most active with?"
    - "What does my application pipeline look like?"

OOP Concepts Demonstrated:
    1. **Encapsulation**: All analytics logic is hidden behind clean
       public methods. The caller doesn't know or care whether stats
       come from SQL aggregation or in-memory computation.
    2. **Data Classes as Value Objects**: The result dataclasses are
       immutable value objects — they carry data but have no behavior
       or identity. Two `PipelineStats` with the same values are
       semantically equal.
    3. **Tell, Don't Ask**: Instead of exposing raw data and letting
       the caller compute stats, this service computes and returns
       ready-to-display results.
"""

from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import Counter

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.application import Application
from app.models.job import Job
from app.models.company import Company


@dataclass
class PipelineStats:
    """Snapshot of the user's application pipeline."""
    total: int = 0
    by_status: Dict[str, int] = field(default_factory=dict)
    success_rate: float = 0.0          # offered or accepted / total
    active_rate: float = 0.0           # non-terminal / total
    this_week: int = 0
    this_month: int = 0


@dataclass
class CompanyInsight:
    """Application activity with a specific company."""
    company_name: str = ""
    company_id: int = 0
    application_count: int = 0
    statuses: Dict[str, int] = field(default_factory=dict)
    latest_application_date: Optional[datetime] = None


@dataclass
class TimelineEntry:
    """A single point on the application timeline."""
    date: str = ""          # ISO date string
    count: int = 0
    cumulative: int = 0


@dataclass
class TrackerDashboard:
    """Complete dashboard data for the frontend."""
    pipeline: PipelineStats = field(default_factory=PipelineStats)
    top_companies: List[CompanyInsight] = field(default_factory=list)
    timeline: List[TimelineEntry] = field(default_factory=list)
    recent_activity: List[Dict] = field(default_factory=list)


class ApplicationTrackerService:
    """
    Computes analytics and insights from application data.

    Follows the Facade pattern: provides a single `get_dashboard()`
    method that internally orchestrates multiple queries and
    computations, returning a ready-to-render dashboard.
    """

    # Terminal statuses — these applications are "done"
    TERMINAL_STATUSES = {"accepted", "rejected", "withdrawn"}
    SUCCESS_STATUSES = {"offered", "accepted"}

    def __init__(self, db: Session):
        self._db = db

    # ── Public API ───────────────────────────────────────────────

    def get_dashboard(self, user_id: int) -> TrackerDashboard:
        """
        Generate the complete application tracker dashboard.

        This is the main entry point — the frontend calls one endpoint
        and gets everything it needs in a single response.
        """
        return TrackerDashboard(
            pipeline=self.get_pipeline_stats(user_id),
            top_companies=self.get_top_companies(user_id, limit=5),
            timeline=self.get_application_timeline(user_id, days=30),
            recent_activity=self.get_recent_activity(user_id, limit=10),
        )

    def get_pipeline_stats(self, user_id: int) -> PipelineStats:
        """
        Compute pipeline statistics using SQL aggregation.

        SQL GROUP BY is used instead of loading all rows and counting
        in Python — this is O(n) at the database level with index
        support, vs O(n) in Python with network + serialization overhead.
        """
        # Count by status using GROUP BY
        status_counts = (
            self._db.query(Application.status, func.count(Application.id))
            .filter(Application.user_id == user_id)
            .group_by(Application.status)
            .all()
        )
        by_status = dict(status_counts)
        total = sum(by_status.values())

        if total == 0:
            return PipelineStats()

        # Success rate
        success_count = sum(
            by_status.get(s, 0) for s in self.SUCCESS_STATUSES
        )
        success_rate = round((success_count / total) * 100, 1)

        # Active rate (non-terminal)
        active_count = sum(
            count for status, count in by_status.items()
            if status not in self.TERMINAL_STATUSES
        )
        active_rate = round((active_count / total) * 100, 1)

        # This week / this month
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        this_week = (
            self._db.query(func.count(Application.id))
            .filter(
                Application.user_id == user_id,
                Application.created_at >= week_ago,
            )
            .scalar()
        )

        this_month = (
            self._db.query(func.count(Application.id))
            .filter(
                Application.user_id == user_id,
                Application.created_at >= month_ago,
            )
            .scalar()
        )

        return PipelineStats(
            total=total,
            by_status=by_status,
            success_rate=success_rate,
            active_rate=active_rate,
            this_week=this_week or 0,
            this_month=this_month or 0,
        )

    def get_top_companies(self, user_id: int, limit: int = 5) -> List[CompanyInsight]:
        """
        Find the companies the user has applied to most frequently.

        Uses a JOIN across three tables (applications → jobs → companies)
        and GROUP BY for aggregation — demonstrating relational algebra
        concepts (join, projection, grouping).
        """
        # Get all user applications with job and company info
        applications = (
            self._db.query(Application)
            .options(
                joinedload(Application.job).joinedload(Job.company)
            )
            .filter(Application.user_id == user_id)
            .all()
        )

        # Group by company
        company_map: Dict[int, CompanyInsight] = {}
        for app in applications:
            if not app.job or not app.job.company:
                continue

            company = app.job.company
            if company.id not in company_map:
                company_map[company.id] = CompanyInsight(
                    company_name=company.name,
                    company_id=company.id,
                )

            insight = company_map[company.id]
            insight.application_count += 1
            insight.statuses[app.status] = insight.statuses.get(app.status, 0) + 1

            if (
                insight.latest_application_date is None
                or app.created_at > insight.latest_application_date
            ):
                insight.latest_application_date = app.created_at

        # Sort by application count and return top N
        sorted_companies = sorted(
            company_map.values(),
            key=lambda c: c.application_count,
            reverse=True,
        )
        return sorted_companies[:limit]

    def get_application_timeline(
        self, user_id: int, days: int = 30
    ) -> List[TimelineEntry]:
        """
        Generate a daily application count for the last N days.

        Returns a list of TimelineEntry objects suitable for
        rendering a line/bar chart on the frontend.
        """
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)

        # Get application dates
        applications = (
            self._db.query(Application.applied_on)
            .filter(
                Application.user_id == user_id,
                Application.created_at >= start_date,
            )
            .all()
        )

        # Count by date
        date_counter = Counter()
        for (applied_on,) in applications:
            if applied_on:
                date_counter[applied_on.isoformat()] += 1

        # Build timeline with all dates (fill gaps with 0)
        timeline = []
        cumulative = 0
        for i in range(days + 1):
            current_date = (start_date + timedelta(days=i)).date()
            date_str = current_date.isoformat()
            count = date_counter.get(date_str, 0)
            cumulative += count
            timeline.append(TimelineEntry(
                date=date_str,
                count=count,
                cumulative=cumulative,
            ))

        return timeline

    def get_recent_activity(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get the most recent application activity for the user.

        Returns simple dicts (not ORM objects) for easy serialization.
        """
        applications = (
            self._db.query(Application)
            .options(
                joinedload(Application.job).joinedload(Job.company)
            )
            .filter(Application.user_id == user_id)
            .order_by(Application.updated_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "application_id": app.id,
                "job_title": app.job.title if app.job else "Unknown",
                "company_name": app.job.company.name if app.job and app.job.company else "Unknown",
                "status": app.status,
                "applied_on": app.applied_on.isoformat() if app.applied_on else None,
                "updated_at": app.updated_at.isoformat() if app.updated_at else None,
            }
            for app in applications
        ]
