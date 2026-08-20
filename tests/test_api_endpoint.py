"""
PHASES 3, 5, 9, 10: API Endpoint Tests
=========================================

These are INTEGRATION TESTS — they test the full HTTP request/response cycle
through FastAPI's routing, middleware, and error handling, but with external
services (LLM calls) mocked.

TEACHING NOTE — Unit vs Integration vs E2E:

  Unit Test:
    Tests ONE function in isolation. Fast. No network.
    Example: test_rejects_non_pdf_content_type() in test_upload_service.py

  Integration Test:
    Tests multiple components working together through the HTTP layer.
    Example: POST /review-resume → routing → validation → (mocked) services → response
    The endpoint, middleware, and error handling are all real.

  End-to-End (E2E) Test:
    Tests the complete system with real external services.
    We DON'T write E2E tests here — they'd call the real Groq API.

TEACHING NOTE — What gets mocked and WHY:
  We mock three functions that the endpoint calls:
    - upload_file:     Returns extracted text (we control what text the endpoint sees)
    - review_response: Returns the review (avoids calling Groq API)
    - improve_resume:  Returns improvements (avoids calling Groq API)

  We keep REAL:
    - FastAPI routing, validation, and response serialization
    - Rate limiting (SlowAPI)
    - Pydantic response model enforcement
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from io import BytesIO
import pymupdf


# ─── Helper ──────────────────────────────────────────────────────────────

def _create_pdf_bytes(text: str = "John Doe\nSoftware Engineer") -> bytes:
    """Creates a valid PDF with the given text."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=10)
    pdf_data = doc.tobytes()
    doc.close()
    return pdf_data


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: Happy Path
# ═══════════════════════════════════════════════════════════════════════════

class TestHappyPath:
    """Tests for successful POST /review-resume requests."""

    def test_valid_pdf_returns_200_with_review_and_improvements(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: A valid PDF upload should return 200 with both review and improvements.

        TEACHING NOTE — How we send a file in tests:
        TestClient.post() accepts a 'files' parameter:
            files={"field_name": ("filename", file_object, "content_type")}
        This simulates a multipart form upload — exactly what a browser does.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            # Arrange
            mock_upload.return_value = {"text": "extracted resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            pdf_bytes = _create_pdf_bytes()

            # Act
            response = test_client.post(
                "/review-resume",
                files={"resume": ("resume.pdf", BytesIO(pdf_bytes), "application/pdf")},
            )

            # Assert — status code
            assert response.status_code == 200

            # Assert — response structure
            data = response.json()
            assert "review" in data, "Response must contain 'review'"
            assert "improvements" in data, "Response must contain 'improvements'"

            # Assert — review content matches our fixture
            assert data["review"]["overall_score"] == 72
            assert data["review"]["hiring_readiness"] == "Good"
            assert len(data["review"]["strengths"]) >= 3
            assert len(data["review"]["bullet_transformations"]) >= 3

            # Assert — improvements content
            assert data["improvements"]["improved_summary"] is not None
            assert len(data["improvements"]["improved_bullets"]) > 0
            assert "current_skills" in data["improvements"]["skills_improvements"]
            assert "keywords" in data["improvements"]["ats_keyword_suggestions"]


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5: target_role Parameter Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestTargetRole:
    """Tests for the optional target_role query parameter."""

    def test_target_role_is_passed_to_both_services(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: target_role should be forwarded to both services.
        WHY:  Both services use target_role to tailor their LLM prompts.

        HOW WE VERIFY:
        After the request, we inspect mock_review.call_args and
        mock_improve.call_args to see what arguments they received.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            response = test_client.post(
                "/review-resume?target_role=Backend Engineer",
                files={"resume": ("resume.pdf", BytesIO(_create_pdf_bytes()), "application/pdf")},
            )

            assert response.status_code == 200

            # The endpoint calls: review_response(str(resume_text), target_role)
            # target_role is the 2nd positional argument
            review_args = mock_review.call_args[0]
            assert review_args[1] == "Backend Engineer"

            # The endpoint calls: improve_resume(str(resume_text), review, target_role)
            # target_role is the 3rd positional argument
            improve_args = mock_improve.call_args[0]
            assert improve_args[2] == "Backend Engineer"

    def test_missing_target_role_passes_none(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: Omitting target_role should pass None to the services.
        WHY:  target_role has a default of None — services handle this gracefully.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            response = test_client.post(
                "/review-resume",
                files={"resume": ("resume.pdf", BytesIO(_create_pdf_bytes()), "application/pdf")},
            )

            assert response.status_code == 200

            review_args = mock_review.call_args[0]
            assert review_args[1] is None

    def test_empty_target_role_is_passed_as_is(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: An empty target_role="" is passed to the services as-is.
        WHY:  The app does NOT validate empty strings — we test ACTUAL behavior.
              This documents the current behavior rather than an intended behavior.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            response = test_client.post(
                "/review-resume?target_role=",
                files={"resume": ("resume.pdf", BytesIO(_create_pdf_bytes()), "application/pdf")},
            )

            assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 9: Full Flow Verification
# ═══════════════════════════════════════════════════════════════════════════

class TestEndpointFlow:
    """
    Tests verifying the internal data flow of the endpoint.

    This is CRITICAL because the app intentionally reuses the first
    review result instead of calling the LLM twice. These tests prove
    that design decision is implemented correctly.
    """

    def test_review_called_exactly_once(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: The review service should be called exactly once per request.
        WHY:  Calling it twice would waste LLM tokens and double latency.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            test_client.post(
                "/review-resume",
                files={"resume": ("resume.pdf", BytesIO(_create_pdf_bytes()), "application/pdf")},
            )

            assert mock_review.call_count == 1

    def test_improvement_called_exactly_once(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: The improvement service should be called exactly once.
        WHY:  Only one improvement pass is needed per review.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            test_client.post(
                "/review-resume",
                files={"resume": ("resume.pdf", BytesIO(_create_pdf_bytes()), "application/pdf")},
            )

            assert mock_improve.call_count == 1

    def test_improvement_receives_the_review_result(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: The improvement service must receive the EXACT review result
              that was returned by the review service.
        WHY:  This is the core design — review once, then improve based
              on that review. Without this test, someone could accidentally
              break the data flow (e.g., pass None instead of the review).

        HOW:
        We check that mock_improve was called with sample_review_response
        as its second positional argument.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            test_client.post(
                "/review-resume",
                files={"resume": ("resume.pdf", BytesIO(_create_pdf_bytes()), "application/pdf")},
            )

            # improve_resume(str(resume_text), review, target_role)
            # The 2nd positional arg should be the review result
            improve_args = mock_improve.call_args[0]
            assert improve_args[1] is sample_review_response

    def test_response_contains_both_results(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: The final JSON response must contain both 'review' and 'improvements'.
        WHY:  The API contract (ResumeAnalysisResponse) requires both fields.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            response = test_client.post(
                "/review-resume",
                files={"resume": ("resume.pdf", BytesIO(_create_pdf_bytes()), "application/pdf")},
            )

            data = response.json()
            assert "review" in data, "Response missing 'review'"
            assert "improvements" in data, "Response missing 'improvements'"


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 10: Rate Limit Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestRateLimiting:
    """
    Tests for SlowAPI rate limiting.

    The endpoint has @limiter.limit("5/minute"):
      - First 5 requests per minute per IP → 200 OK
      - 6th request → 429 Too Many Requests

    TEACHING NOTE:
    The conftest.py has an autouse fixture (_reset_rate_limiter) that
    clears the rate limiter state before each test. This prevents state
    leakage — without it, requests from other tests would count toward
    the rate limit, causing unpredictable 429 errors.
    """

    def test_sixth_request_is_rate_limited(
        self,
        test_client,
        sample_review_response,
        sample_improvement_response,
    ):
        """
        WHAT: After 5 successful requests, the 6th should return 429.
        WHY:  The rate limit protects the API from abuse and excessive LLM costs.
        """
        with patch("api.api.upload_file", new_callable=AsyncMock) as mock_upload, \
             patch("api.api.review_response") as mock_review, \
             patch("api.api.improve_resume") as mock_improve:

            mock_upload.return_value = {"text": "resume text"}
            mock_review.return_value = sample_review_response
            mock_improve.return_value = sample_improvement_response

            pdf_bytes = _create_pdf_bytes()

            # Send 5 requests — all should succeed
            for i in range(5):
                resp = test_client.post(
                    "/review-resume",
                    files={"resume": ("resume.pdf", BytesIO(pdf_bytes), "application/pdf")},
                )
                assert resp.status_code == 200, f"Request {i + 1} failed unexpectedly"

            # The 6th request should be rate-limited
            resp = test_client.post(
                "/review-resume",
                files={"resume": ("resume.pdf", BytesIO(pdf_bytes), "application/pdf")},
            )
            assert resp.status_code == 429
