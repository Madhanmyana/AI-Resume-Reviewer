"""
PHASE 7: Review Service Tests
================================

Tests for resume_review_service.review_response() in isolation.

These are UNIT TESTS — we mock the LLM client so we NEVER call the real
Groq API during testing.

WHY mock the LLM client?
  1. Real API calls cost money (token usage).
  2. Real API calls are slow (network latency).
  3. Real API calls are non-deterministic (LLM output varies each time).
  4. Real API calls need internet access.
  5. Real API calls can fail due to external outages.
  6. We're testing OUR code, not Groq's service.

TEACHING NOTE — The "patch where it's USED" principle:
  The OpenAI `client` is DEFINED in services/resume_review_service.py.
  When we mock it, we patch "services.resume_review_service.client"
  because that's where it's USED by the function we're testing.

TEACHING NOTE — patch() as context manager:
  with patch("module.name") as mock_thing:
      # Inside this block, "module.name" is replaced by mock_thing
      # After the block, the real object is automatically restored
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import openai

from services.resume_review_service import review_response


# ═══════════════════════════════════════════════════════════════════════════
# Success Cases
# ═══════════════════════════════════════════════════════════════════════════

class TestReviewServiceSuccess:
    """Tests for the happy path of review_response()."""

    def test_returns_parsed_response(self, sample_review_response):
        """
        WHAT: When the LLM returns valid data, review_response() should
              return the parsed ResumeReviewResponse.

        Arrange: Mock the client to return a pre-built response
        Act:     Call review_response() with test resume text
        Assert:  The returned object matches our sample response
        """
        with patch("services.resume_review_service.client") as mock_client:
            # Arrange: Make the mock return our fixture
            mock_api_response = MagicMock()
            mock_api_response.output_parsed = sample_review_response
            mock_client.responses.parse.return_value = mock_api_response

            # Act
            result = review_response("John Doe\nSoftware Engineer\n")

            # Assert
            assert result == sample_review_response
            assert result.overall_score == 72
            mock_client.responses.parse.assert_called_once()

    def test_works_without_target_role(self, sample_review_response):
        """
        WHAT: review_response() should work when target_role is None.
        WHY:  target_role is optional — review works for any resume.
        """
        with patch("services.resume_review_service.client") as mock_client:
            mock_api_response = MagicMock()
            mock_api_response.output_parsed = sample_review_response
            mock_client.responses.parse.return_value = mock_api_response

            result = review_response("resume text", target_role=None)

            assert result == sample_review_response
            mock_client.responses.parse.assert_called_once()

    def test_passes_correct_model(self, sample_review_response):
        """
        WHAT: The service should use the correct LLM model.
        WHY:  Using the wrong model would change behavior and costs.
        """
        with patch("services.resume_review_service.client") as mock_client:
            mock_api_response = MagicMock()
            mock_api_response.output_parsed = sample_review_response
            mock_client.responses.parse.return_value = mock_api_response

            review_response("resume text")

            # Verify the model argument
            call_kwargs = mock_client.responses.parse.call_args.kwargs
            assert call_kwargs["model"] == "openai/gpt-oss-20b"


# ═══════════════════════════════════════════════════════════════════════════
# Error Handling Cases
# ═══════════════════════════════════════════════════════════════════════════

class TestReviewServiceErrors:
    """
    Tests for error handling in review_response().

    Each OpenAI error type should be caught and converted to an
    HTTPException with the correct status code and message.
    This is critical — without these handlers, unhandled exceptions
    would return a generic 500 to the user with no useful information.
    """

    def test_authentication_error_returns_500(self):
        """
        AuthenticationError → HTTPException(500)
        WHY: Bad API credentials are a server-side config issue, not the user's fault.
        """
        with patch("services.resume_review_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.AuthenticationError(
                message="Invalid API key",
                response=MagicMock(status_code=401),
                body=None,
            )

            with pytest.raises(HTTPException) as exc_info:
                review_response("resume text")

            assert exc_info.value.status_code == 500
            assert "credentials are invalid" in exc_info.value.detail

    def test_rate_limit_error_returns_429(self):
        """
        RateLimitError → HTTPException(429)
        WHY: Groq is rate-limiting us — tell the user to retry later.
        """
        with patch("services.resume_review_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.RateLimitError(
                message="Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None,
            )

            with pytest.raises(HTTPException) as exc_info:
                review_response("resume text")

            assert exc_info.value.status_code == 429
            assert "rate-limited" in exc_info.value.detail

    def test_connection_error_returns_500(self):
        """
        APIConnectionError → HTTPException(500)
        WHY: Can't reach the API — network issue.
        """
        with patch("services.resume_review_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.APIConnectionError(
                request=MagicMock(),
            )

            with pytest.raises(HTTPException) as exc_info:
                review_response("resume text")

            assert exc_info.value.status_code == 500
            assert "connection error" in exc_info.value.detail

    def test_generic_api_error_returns_500(self):
        """
        APIError (catch-all) → HTTPException(500)
        WHY: Catches any unexpected API failure gracefully.
        """
        with patch("services.resume_review_service.client") as mock_client:
            mock_client.responses.parse.side_effect = openai.APIError(
                message="Something went wrong",
                request=MagicMock(),
                body=None,
            )

            with pytest.raises(HTTPException) as exc_info:
                review_response("resume text")

            assert exc_info.value.status_code == 500
            assert "temporarily unavailable" in exc_info.value.detail
