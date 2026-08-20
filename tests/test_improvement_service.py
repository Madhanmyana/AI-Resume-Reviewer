"""
PHASE 8: Improvement Service Tests
=====================================

Tests for resume_improvement_service.improve_resume() in isolation.

TEACHING NOTE — Why a separate test file from the review service?
  The improvement service has a critical dependency: it receives the
  REVIEW result as input. We must verify:
    1. It accepts the review response correctly.
    2. It includes the review data in the LLM prompt.
    3. It handles target_role independently.
    4. It has its own error handling (same pattern, different import path).

CRITICAL TEACHING MOMENT — "Patch where it's USED":
  The improvement service imports `client` FROM the review service:
      from services.resume_review_service import client

  This creates a NEW reference to the client object in the improvement
  service's namespace. To mock it, we MUST patch:
      "services.resume_improvement_service.client"
  NOT:
      "services.resume_review_service.client"

  If we patched the wrong location, the improvement service would still
  use the REAL client and try to call the actual Groq API!
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import openai

from services.resume_improvement_service import improve_resume


# ═══════════════════════════════════════════════════════════════════════════
# Success Cases
# ═══════════════════════════════════════════════════════════════════════════

class TestImprovementServiceSuccess:
    """Tests for the happy path of improve_resume()."""

    def test_returns_parsed_improvement_response(
        self, sample_review_response, sample_improvement_response
    ):
        """
        WHAT: improve_resume() should return a parsed ResumeImprovementResponse.

        Note: We patch "services.resume_improvement_service.client"
        (where it's USED), not "services.resume_review_service.client"
        (where it was originally defined).
        """
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_api_response = MagicMock()
            mock_api_response.output_parsed = sample_improvement_response
            mock_client.responses.parse.return_value = mock_api_response

            result = improve_resume("resume text", sample_review_response)

            assert result == sample_improvement_response
            mock_client.responses.parse.assert_called_once()

    def test_includes_review_in_prompt(
        self, sample_review_response, sample_improvement_response
    ):
        """
        WHAT: The review result must be included in the improvement prompt.
        WHY:  This is the KEY design decision — reuse the first LLM review,
              don't re-review the resume. The prompt should contain the
              review data so the improvement LLM can build on it.
        """
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_api_response = MagicMock()
            mock_api_response.output_parsed = sample_improvement_response
            mock_client.responses.parse.return_value = mock_api_response

            improve_resume("resume text", sample_review_response)

            # Verify the prompt contains the review markers
            call_kwargs = mock_client.responses.parse.call_args.kwargs
            prompt_sent = call_kwargs["input"]
            assert "resume review starts here" in prompt_sent
            assert "resume review ends here" in prompt_sent

    def test_includes_target_role_when_provided(
        self, sample_review_response, sample_improvement_response
    ):
        """
        WHAT: target_role should appear in the prompt when provided.
        WHY:  The LLM uses it to tailor improvement suggestions.
        """
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_api_response = MagicMock()
            mock_api_response.output_parsed = sample_improvement_response
            mock_client.responses.parse.return_value = mock_api_response

            improve_resume(
                "resume text", sample_review_response, target_role="Backend Engineer"
            )

            call_kwargs = mock_client.responses.parse.call_args.kwargs
            assert "Backend Engineer" in call_kwargs["input"]

    def test_works_without_target_role(
        self, sample_review_response, sample_improvement_response
    ):
        """target_role=None should still produce a valid response."""
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_api_response = MagicMock()
            mock_api_response.output_parsed = sample_improvement_response
            mock_client.responses.parse.return_value = mock_api_response

            result = improve_resume("resume text", sample_review_response, target_role=None)

            assert result == sample_improvement_response


# ═══════════════════════════════════════════════════════════════════════════
# Error Handling Cases
# ═══════════════════════════════════════════════════════════════════════════

class TestImprovementServiceErrors:
    """
    Same error pattern as the review service, but patched at
    "services.resume_improvement_service.client" — the USAGE location.
    """

    def test_authentication_error_returns_500(self, sample_review_response):
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.AuthenticationError(
                message="Invalid API key",
                response=MagicMock(status_code=401),
                body=None,
            )

            with pytest.raises(HTTPException) as exc_info:
                improve_resume("resume text", sample_review_response)

            assert exc_info.value.status_code == 500
            assert "credentials are invalid" in exc_info.value.detail

    def test_rate_limit_error_returns_429(self, sample_review_response):
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.RateLimitError(
                message="Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None,
            )

            with pytest.raises(HTTPException) as exc_info:
                improve_resume("resume text", sample_review_response)

            assert exc_info.value.status_code == 429
            assert "rate-limited" in exc_info.value.detail

    def test_connection_error_returns_500(self, sample_review_response):
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.APIConnectionError(
                request=MagicMock(),
            )

            with pytest.raises(HTTPException) as exc_info:
                improve_resume("resume text", sample_review_response)

            assert exc_info.value.status_code == 500
            assert "connection error" in exc_info.value.detail

    def test_generic_api_error_returns_500(self, sample_review_response):
        with patch("services.resume_improvement_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.APIError(
                message="Something went wrong",
                request=MagicMock(),
                body=None,
            )

            with pytest.raises(HTTPException) as exc_info:
                improve_resume("resume text", sample_review_response)

            assert exc_info.value.status_code == 500
            assert "temporarily unavailable" in exc_info.value.detail
