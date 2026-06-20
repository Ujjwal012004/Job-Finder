"""
End-to-End API Test Script — Phase 4 Verification.

This script tests the complete data flow:
    Database → Repository → Service → Route → HTTP Response

It verifies:
    1. Health check
    2. User registration & login
    3. Job seeding via the data service
    4. Job search (public + authenticated)
    5. Job CRUD operations
    6. Application creation & tracking
    7. Saving/bookmarking jobs
    8. Dashboard analytics
    9. Aggregation endpoint
   10. Recommendations

Run with:
    cd backend
    python -m pytest tests/test_api.py -v
    OR
    python tests/test_api.py  (standalone)
"""

import sys
import os

# Add backend to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine


# ── Test Client Setup ────────────────────────────────────────────
# Create fresh tables for testing
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ── Helper State ─────────────────────────────────────────────────
test_state = {
    "token": None,
    "user_id": None,
    "job_id": None,
    "company_id": None,
    "application_id": None,
    "saved_job_id": None,
}


def auth_header():
    """Return Authorization header dict."""
    return {"Authorization": f"Bearer {test_state['token']}"}


def section(title: str):
    """Print a section divider."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_result(name: str, passed: bool, detail: str = ""):
    """Print a test result."""
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status}  {name}"
    if detail:
        msg += f"  ->  {detail}"
    print(msg)
    return passed


# ══════════════════════════════════════════════════════════════════
# TEST SUITE
# ══════════════════════════════════════════════════════════════════

def run_all_tests():
    """Execute all tests in sequence."""
    passed = 0
    failed = 0
    total = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if test_result(name, condition, detail):
            passed += 1
        else:
            failed += 1

    # ── 1. Health Check ──────────────────────────────────────────
    section("1. Health Check")
    r = client.get("/")
    check("GET / returns 200", r.status_code == 200)
    check("Response has status=healthy", r.json().get("status") == "healthy")

    # ── 2. User Registration ─────────────────────────────────────
    section("2. User Registration")
    r = client.post("/api/auth/register", json={
        "email": "testuser@jobfinder.com",
        "password": "SecurePass123!",
        "full_name": "Test User",
        "phone": "+1234567890",
    })
    check("Register returns 201", r.status_code == 201, f"status={r.status_code}")
    if r.status_code == 201:
        data = r.json()
        test_state["user_id"] = data["id"]
        check("User has ID", data.get("id") is not None, f"id={data['id']}")
        check("Email matches", data.get("email") == "testuser@jobfinder.com")
        check("Password hash NOT exposed", "password_hash" not in data)

    # Duplicate registration should fail
    r = client.post("/api/auth/register", json={
        "email": "testuser@jobfinder.com",
        "password": "AnotherPass",
        "full_name": "Duplicate User",
    })
    check("Duplicate email returns 400", r.status_code == 400)

    # ── 3. User Login ────────────────────────────────────────────
    section("3. User Login")
    r = client.post("/api/auth/login", json={
        "email": "testuser@jobfinder.com",
        "password": "SecurePass123!",
    })
    check("Login returns 200", r.status_code == 200)
    if r.status_code == 200:
        data = r.json()
        test_state["token"] = data["access_token"]
        check("Token received", data.get("access_token") is not None)
        check("Token type is bearer", data.get("token_type") == "bearer")

    # Bad password should fail
    r = client.post("/api/auth/login", json={
        "email": "testuser@jobfinder.com",
        "password": "WrongPassword",
    })
    check("Wrong password returns 401", r.status_code == 401)

    # ── 4. User Profile ─────────────────────────────────────────
    section("4. User Profile")
    r = client.get("/api/users/me", headers=auth_header())
    check("GET /me returns 200", r.status_code == 200)
    check("Profile has full_name", r.json().get("full_name") == "Test User")

    r = client.put("/api/users/me", headers=auth_header(), json={
        "full_name": "Updated Test User",
    })
    check("Profile update returns 200", r.status_code == 200)
    check("Name updated", r.json().get("full_name") == "Updated Test User")

    # ── 5. Seed Data ─────────────────────────────────────────────
    section("5. Seed Sample Data (JobDataService)")
    r = client.post("/api/seed/jobs")
    check("Seed returns 200", r.status_code == 200)
    data = r.json()
    check("Jobs created > 0", data.get("created", 0) > 0, f"created={data.get('created')}")
    check("No errors", len(data.get("errors", [])) == 0)

    # Run seed again — should be idempotent
    r = client.post("/api/seed/jobs")
    data2 = r.json()
    check("Re-seed is idempotent (0 new)", data2.get("created") == 0, f"created={data2.get('created')}")
    check("All duplicates skipped", data2.get("skipped_duplicate", 0) > 0)

    # ── 6. Company CRUD ──────────────────────────────────────────
    section("6. Company CRUD")
    r = client.get("/api/companies/")
    check("List companies returns 200", r.status_code == 200)
    companies = r.json()
    check("Companies seeded", len(companies) > 0, f"count={len(companies)}")
    if companies:
        test_state["company_id"] = companies[0]["id"]

    r = client.get(f"/api/companies/{test_state['company_id']}")
    check("Get company by ID", r.status_code == 200)

    # ── 7. Job Search (Public) ───────────────────────────────────
    section("7. Job Search (Public — No Auth)")
    r = client.get("/api/search/jobs")
    check("Public search returns 200", r.status_code == 200)
    data = r.json()
    check("Results returned", data.get("total_count", 0) > 0, f"total={data.get('total_count')}")
    check("Results have relevance_score", all(
        "relevance_score" in res for res in data.get("results", [])
    ))

    # Search with keyword filter
    r = client.get("/api/search/jobs?keyword=Python")
    data = r.json()
    check("Keyword search works", r.status_code == 200)
    check("Keyword filter applied", "keyword" in data.get("filters_applied", {}))

    # Search with multiple filters
    r = client.get("/api/search/jobs?is_remote=true&employment_type=full-time")
    data = r.json()
    check("Multi-filter search works", r.status_code == 200)

    # ── 8. Job CRUD ──────────────────────────────────────────────
    section("8. Job CRUD")
    r = client.get("/api/jobs/")
    check("List jobs returns 200", r.status_code == 200)
    jobs = r.json()
    if jobs:
        test_state["job_id"] = jobs[0]["id"]

    r = client.get(f"/api/jobs/{test_state['job_id']}")
    check("Get job by ID", r.status_code == 200)
    check("Job has company data", r.json().get("company") is not None)

    # ── 9. Aggregations ──────────────────────────────────────────
    section("9. Job Aggregations")
    r = client.get("/api/search/aggregations")
    check("Aggregations return 200", r.status_code == 200)
    data = r.json()
    check("Total jobs > 0", data.get("total_jobs", 0) > 0)
    check("Has employment_type breakdown", len(data.get("by_employment_type", {})) > 0)
    check("Has remote count", "remote_count" in data)

    # ── 10. Apply to Job ─────────────────────────────────────────
    section("10. Job Application (Authenticated)")
    r = client.post("/api/applications", headers=auth_header(), json={
        "job_id": test_state["job_id"],
        "cover_letter": "I am excited to apply for this position.",
    })
    check("Application created (201)", r.status_code == 201)
    if r.status_code == 201:
        test_state["application_id"] = r.json()["id"]
        check("Application has status=applied", r.json().get("status") == "applied")

    # Duplicate application should fail
    r = client.post("/api/applications", headers=auth_header(), json={
        "job_id": test_state["job_id"],
    })
    check("Duplicate application rejected (400)", r.status_code == 400)

    # List applications
    r = client.get("/api/applications", headers=auth_header())
    check("List applications returns 200", r.status_code == 200)
    check("Has at least 1 application", len(r.json()) >= 1)

    # Update application status
    r = client.put(
        f"/api/applications/{test_state['application_id']}",
        headers=auth_header(),
        json={"status": "interviewing"},
    )
    check("Application status updated", r.status_code == 200)
    check("Status is now 'interviewing'", r.json().get("status") == "interviewing")

    # ── 11. Application Notes ────────────────────────────────────
    section("11. Application Notes")
    r = client.post(
        f"/api/applications/{test_state['application_id']}/notes",
        headers=auth_header(),
        json={"content": "Prepared for technical interview", "note_type": "interview_prep"},
    )
    check("Note created (201)", r.status_code == 201)
    check("Note type correct", r.json().get("note_type") == "interview_prep")

    r = client.get(
        f"/api/applications/{test_state['application_id']}/notes",
        headers=auth_header(),
    )
    check("List notes returns 200", r.status_code == 200)
    check("Has at least 1 note", len(r.json()) >= 1)

    # ── 12. Save/Bookmark Job ────────────────────────────────────
    section("12. Saved Jobs (Bookmarks)")
    # Find a job we haven't applied to
    all_jobs = client.get("/api/jobs/").json()
    second_job_id = all_jobs[1]["id"] if len(all_jobs) > 1 else all_jobs[0]["id"]

    r = client.post("/api/saved-jobs", headers=auth_header(), json={
        "job_id": second_job_id,
    })
    check("Job saved (201)", r.status_code == 201)
    if r.status_code == 201:
        test_state["saved_job_id"] = r.json()["id"]

    r = client.get("/api/saved-jobs", headers=auth_header())
    check("List saved jobs returns 200", r.status_code == 200)
    check("Has at least 1 saved job", len(r.json()) >= 1)

    # ── 13. Authenticated Search (with context) ──────────────────
    section("13. Authenticated Search (with user context)")
    r = client.get("/api/search/jobs", headers=auth_header())
    check("Auth search returns 200", r.status_code == 200)
    data = r.json()
    # Check if any result has is_saved or has_applied flags
    results = data.get("results", [])
    has_context = any(r.get("is_saved") or r.get("has_applied") for r in results)
    check("Results enriched with user context", has_context)

    # ── 14. Dashboard ────────────────────────────────────────────
    section("14. Dashboard Analytics")
    r = client.get("/api/dashboard/", headers=auth_header())
    check("Dashboard returns 200", r.status_code == 200)
    data = r.json()
    check("Has pipeline stats", "pipeline" in data)
    check("Pipeline total > 0", data["pipeline"].get("total", 0) > 0)
    check("Has timeline", len(data.get("timeline", [])) > 0)
    check("Has recent activity", len(data.get("recent_activity", [])) > 0)

    # Pipeline stats endpoint
    r = client.get("/api/dashboard/pipeline", headers=auth_header())
    check("Pipeline endpoint returns 200", r.status_code == 200)

    # ── 15. Recommendations ──────────────────────────────────────
    section("15. Recommendations")
    r = client.get("/api/search/recommendations", headers=auth_header())
    check("Recommendations return 200", r.status_code == 200)
    recs = r.json()
    check("Recommendations returned", len(recs) > 0, f"count={len(recs)}")

    # ── 16. Cleanup — Delete operations ──────────────────────────
    section("16. Cleanup & Delete Operations")
    if test_state["saved_job_id"]:
        r = client.delete(f"/api/saved-jobs/{test_state['saved_job_id']}", headers=auth_header())
        check("Unsave job (204)", r.status_code == 204)

    if test_state["application_id"]:
        r = client.delete(
            f"/api/applications/{test_state['application_id']}",
            headers=auth_header(),
        )
        check("Delete application (204)", r.status_code == 204)

    # ── SUMMARY ──────────────────────────────────────────────────
    section("TEST SUMMARY")
    print(f"\n  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Rate:   {(passed/total)*100:.1f}%\n")

    return failed == 0


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n>>> Job Finder API - End-to-End Test Suite")
    print("=" * 60)
    success = run_all_tests()
    sys.exit(0 if success else 1)
