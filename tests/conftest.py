"""
conftest.py — Shared Test Fixtures
====================================

TEACHING NOTE — What is conftest.py?
conftest.py is a special pytest file. Any fixture defined here is automatically
available to ALL test files in the same directory (no import needed).
Think of it as a "shared toolbox" for your tests.

TEACHING NOTE — What is a fixture?
A fixture is a function decorated with @pytest.fixture that provides
test data or setup/teardown logic. Instead of repeating setup code
in every test, you define it once as a fixture, and pytest injects it
automatically when a test function lists it as a parameter.

Fixture Scopes:
  - function (default): Created fresh for EACH test. Safest, most isolated.
  - module: Created once per test file.
  - session: Created once for the entire test run.

We use function scope by default to keep tests fully isolated from each other.
"""

import os

# ─── CRITICAL: Set a fake API key BEFORE any app modules are imported ────
#
# WHY: The review service creates an OpenAI client at MODULE LEVEL:
#     client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), ...)
#
# When pytest imports our app code, this line runs immediately.
# If GROQ_API_KEY is missing, OpenAI() raises an error and tests crash
# before they even start.
#
# os.environ.setdefault() only sets the var if it's NOT already present,
# so if you have a real .env file, it won't be overridden.
# This fake key is never used for real API calls — we mock those in tests.
os.environ.setdefault("GROQ_API_KEY", "test-fake-key-not-real")

import pytest
import pymupdf
from fastapi.testclient import TestClient

# Now safe to import app modules (the fake key prevents OpenAI() from crashing)
from main import app
from schemas.resume_review_schema import (
    ResumeReviewResponse,
    CategoryScores,
    BulletTransformation,
    ATSSuggestions,
    PrioritizedActionPlan,
    SectionAnalysis,
)
from schemas.resume_improvement_schema import (
    ResumeImprovementResponse,
    ImprovedBullet,
    SkillsImprovement,
    ATSKeywordSuggestions,
)


# ═══════════════════════════════════════════════════════════════════════════
# INFRASTRUCTURE FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def test_client():
    """
    Creates a FastAPI TestClient for sending HTTP requests in tests.

    TEACHING NOTE:
    TestClient wraps your FastAPI app and lets you call endpoints
    (GET, POST, etc.) without starting a real server or opening a browser.
    It handles async endpoints transparently — your test code stays synchronous.

    Usage in a test:
        def test_something(test_client):
            response = test_client.get("/health")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """
    Reset rate limiter state BEFORE each test to prevent state leakage.

    TEACHING NOTE — Why is this needed?
    SlowAPI stores rate-limit counters in memory. Without resetting,
    a test that makes 5 requests would "use up" the quota, causing
    the NEXT test to get an unexpected 429 error.

    autouse=True means this fixture runs automatically for EVERY test,
    even if the test doesn't explicitly request it.
    """
    # Reset BEFORE the test runs (so each test starts with a clean counter)
    try:
        from limiter import limiter as app_limiter
        if hasattr(app_limiter, "_storage") and hasattr(app_limiter._storage, "reset"):
            app_limiter._storage.reset()
    except Exception:
        pass  # Don't fail tests if reset doesn't work
    yield
    # (no teardown needed — we reset at the start of each test)


# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE DATA FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_resume_text():
    """Realistic resume text for testing services."""
    return (
        "John Doe\n"
        "Software Engineer\n"
        "Email: john@example.com | Phone: 555-0123\n\n"
        "EXPERIENCE\n"
        "Senior Software Engineer, Acme Corp (2020-2024)\n"
        "- Built REST APIs serving 10,000 daily users using Python and FastAPI\n"
        "- Reduced deployment time by 40% by implementing CI/CD pipelines\n"
        "- Led a team of 5 engineers to deliver a microservices migration\n\n"
        "Software Engineer, Beta Inc (2017-2020)\n"
        "- Developed internal tools for data processing\n"
        "- Maintained legacy Django applications\n"
        "- Wrote unit tests improving code coverage from 30% to 85%\n\n"
        "SKILLS\n"
        "Python, FastAPI, Django, PostgreSQL, Docker, AWS, Git, CI/CD\n\n"
        "EDUCATION\n"
        "B.S. Computer Science, State University (2017)\n"
    )


@pytest.fixture
def valid_pdf_bytes(sample_resume_text):
    """
    Creates a minimal valid PDF containing resume text.

    TEACHING NOTE:
    Instead of shipping a real PDF file, we generate one programmatically
    using PyMuPDF. This makes the test self-contained and reproducible —
    no external files to manage or accidentally delete.
    """
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), sample_resume_text, fontsize=10)
    pdf_data = doc.tobytes()
    doc.close()
    return pdf_data


@pytest.fixture
def sample_review_response():
    """
    A realistic ResumeReviewResponse matching the actual Pydantic schema.

    TEACHING NOTE:
    This fixture creates a complete, valid response object that matches
    what the real LLM would return (after Pydantic parsing). We use this
    when we need to mock the review service's return value.

    All Field constraints are satisfied:
      - overall_score: 0-100     ✓ (72)
      - strengths: 3-4 items     ✓ (3)
      - weaknesses: 3-4 items    ✓ (3)
      - bullet_transformations: ≥3 ✓ (3)
      - category sub-scores: within their max values ✓
    """
    return ResumeReviewResponse(
        overall_score=72,
        category_scores=CategoryScores(
            ATS_structure=18,
            impact_and_metrics=20,
            language_and_brevity=14,
            skills_and_keywords=20,
        ),
        executive_summary=(
            "The candidate demonstrates solid backend engineering experience "
            "with quantifiable achievements. The resume would benefit from "
            "improved ATS formatting and stronger action verbs."
        ),
        strengths=[
            "Strong quantified achievements in the experience section",
            "Clear technical skill categorization",
            "Logical chronological structure with consistent date formatting",
        ],
        weaknesses=[
            "Missing professional summary section at the top",
            "Some bullets lack measurable outcomes",
            "Skills section does not separate technical from soft skills",
        ],
        ATS_compatibility_suggestions=ATSSuggestions(
            parsing_safety="Use a single-column layout with standard headers.",
            keyword_optimization_strategy="Include both acronyms and full forms.",
        ),
        prioritized_action_plan=PrioritizedActionPlan(
            P0="Add a professional summary.",
            P1="Rewrite weak bullets with X-Y-Z framework.",
            P2="Categorize skills section.",
        ),
        bullet_transformations=[
            BulletTransformation(
                original="Developed internal tools for data processing",
                critique="Vague — no specifics about tools, data, or impact",
                improved="Engineered internal data processing tools using Python",
            ),
            BulletTransformation(
                original="Maintained legacy Django applications",
                critique="Passive maintenance framing with no demonstrated value",
                improved="Maintained and modernized legacy Django applications",
            ),
            BulletTransformation(
                original="Led a team of 5 engineers",
                critique="Missing the business outcome of the migration",
                improved="Led a team of 5 to deliver microservices migration",
            ),
        ],
        hiring_readiness="Good",
        section_analysis=[
            SectionAnalysis(
                section="Experience",
                present=True,
                strengths=["Quantified achievements"],
                weaknesses=["Some bullets lack metrics"],
                recommendations=["Apply X-Y-Z framework"],
            ),
            SectionAnalysis(
                section="Skills",
                present=True,
                strengths=["Relevant skills listed"],
                weaknesses=["No categorization"],
                recommendations=["Group by type"],
            ),
            SectionAnalysis(
                section="Education",
                present=True,
                strengths=["Degree and institution stated"],
                weaknesses=["No coursework mentioned"],
                recommendations=["Add relevant coursework"],
            ),
        ],
    )


@pytest.fixture
def sample_improvement_response():
    """A realistic ResumeImprovementResponse matching the actual Pydantic schema."""
    return ResumeImprovementResponse(
        target_role=None,
        improved_summary=(
            "Results-driven Senior Software Engineer with 7+ years building "
            "scalable backend systems using Python and FastAPI."
        ),
        improved_bullets=[
            ImprovedBullet(
                original="Developed internal tools for data processing",
                improved="Engineered internal data processing tools using Python",
                reason="Added specificity without inventing metrics",
            ),
            ImprovedBullet(
                original="Maintained legacy Django applications",
                improved="Maintained and modernized legacy Django applications",
                reason="Reframed from passive to active improvement",
            ),
        ],
        skills_improvements=SkillsImprovement(
            current_skills=["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "AWS"],
            recommendations=["Group skills by category"],
        ),
        ats_keyword_suggestions=ATSKeywordSuggestions(
            keywords=["Python", "FastAPI", "REST API", "microservices"],
            recommendations=["Include full forms alongside acronyms"],
        ),
    )
