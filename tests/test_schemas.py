"""
PHASE 6: Schema Validation Tests
==================================

WHY test Pydantic schemas separately?
  1. Schemas define your API contract — if a schema breaks, your API breaks.
  2. Schemas have Field constraints (e.g., score 0-100). We must verify they
     actually reject invalid data.
  3. Schema tests are fast, pure Python — no mocking, no I/O, no network.
  4. They catch issues early, before you even test the endpoint.

TEACHING NOTE — pytest.raises:
  When you EXPECT code to raise an exception, wrap it in:
      with pytest.raises(SomeException):
          code_that_should_fail()
  If the exception IS raised → test PASSES.
  If no exception is raised → test FAILS.
"""

import pytest
from pydantic import ValidationError

from schemas.resume_review_schema import (
    ResumeReviewResponse,
    CategoryScores,
    HiringReadiness,
)
from schemas.resume_improvement_schema import (
    ResumeImprovementResponse,
    SkillsImprovement,
    ATSKeywordSuggestions,
)
from schemas.resume_analysis_response_schema import ResumeAnalysisResponse


# ═══════════════════════════════════════════════════════════════════════════
# CategoryScores — Field constraint tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCategoryScores:
    """Tests for CategoryScores with ge/le Field constraints."""

    def test_valid_scores_accepted(self):
        """All scores within their allowed ranges should pass."""
        scores = CategoryScores(
            ATS_structure=20,
            impact_and_metrics=25,
            language_and_brevity=15,
            skills_and_keywords=20,
        )
        assert scores.ATS_structure == 20
        assert scores.impact_and_metrics == 25

    def test_ats_structure_rejects_above_25(self):
        """ATS_structure has Field(le=25) — value 26 must be rejected."""
        with pytest.raises(ValidationError):
            CategoryScores(
                ATS_structure=26,  # MAX is 25
                impact_and_metrics=20,
                language_and_brevity=15,
                skills_and_keywords=20,
            )

    def test_negative_score_rejected(self):
        """All scores have Field(ge=0) — negative values must be rejected."""
        with pytest.raises(ValidationError):
            CategoryScores(
                ATS_structure=-1,
                impact_and_metrics=20,
                language_and_brevity=15,
                skills_and_keywords=20,
            )

    def test_impact_and_metrics_rejects_above_30(self):
        """impact_and_metrics has Field(le=30) — 31 must fail."""
        with pytest.raises(ValidationError):
            CategoryScores(
                ATS_structure=20,
                impact_and_metrics=31,
                language_and_brevity=15,
                skills_and_keywords=20,
            )

    def test_language_and_brevity_rejects_above_20(self):
        """language_and_brevity has Field(le=20) — 21 must fail."""
        with pytest.raises(ValidationError):
            CategoryScores(
                ATS_structure=20,
                impact_and_metrics=25,
                language_and_brevity=21,
                skills_and_keywords=20,
            )

    def test_skills_and_keywords_rejects_above_25(self):
        """skills_and_keywords has Field(le=25) — 26 must fail."""
        with pytest.raises(ValidationError):
            CategoryScores(
                ATS_structure=20,
                impact_and_metrics=25,
                language_and_brevity=15,
                skills_and_keywords=26,
            )


# ═══════════════════════════════════════════════════════════════════════════
# HiringReadiness Enum
# ═══════════════════════════════════════════════════════════════════════════

class TestHiringReadiness:
    """Tests for the HiringReadiness enum values."""

    @pytest.mark.parametrize("value", [
        "Excellent",
        "Good",
        "Needs Improvement",
        "Not Competitive Yet",
    ])
    def test_valid_values_accepted(self, value):
        """
        TEACHING NOTE — @pytest.mark.parametrize:
        Runs the SAME test once for each value in the list.
        This avoids writing 4 nearly identical test functions.
        """
        readiness = HiringReadiness(value)
        assert readiness.value == value

    def test_invalid_value_rejected(self):
        """A value not defined in the enum must raise ValueError."""
        with pytest.raises(ValueError):
            HiringReadiness("Amazing")


# ═══════════════════════════════════════════════════════════════════════════
# ResumeReviewResponse — list length and score constraints
# ═══════════════════════════════════════════════════════════════════════════

class TestResumeReviewResponse:
    """Tests for the complete review response schema."""

    def test_valid_response_passes(self, sample_review_response):
        """A fully valid response created from the fixture should not raise."""
        assert sample_review_response.overall_score == 72
        assert sample_review_response.hiring_readiness == HiringReadiness.Good

    def test_overall_score_rejects_above_100(self):
        """overall_score has Field(le=100) — 101 must fail."""
        data = _minimal_review_data()
        data["overall_score"] = 101
        with pytest.raises(ValidationError):
            ResumeReviewResponse(**data)

    def test_overall_score_rejects_below_0(self):
        """overall_score has Field(ge=0) — negative must fail."""
        data = _minimal_review_data()
        data["overall_score"] = -1
        with pytest.raises(ValidationError):
            ResumeReviewResponse(**data)

    def test_strengths_rejects_fewer_than_3(self):
        """strengths has Field(min_length=3) — 2 items must fail."""
        data = _minimal_review_data()
        data["strengths"] = ["one", "two"]
        with pytest.raises(ValidationError):
            ResumeReviewResponse(**data)

    def test_strengths_rejects_more_than_4(self):
        """strengths has Field(max_length=4) — 5 items must fail."""
        data = _minimal_review_data()
        data["strengths"] = ["a", "b", "c", "d", "e"]
        with pytest.raises(ValidationError):
            ResumeReviewResponse(**data)

    def test_weaknesses_rejects_fewer_than_3(self):
        """weaknesses has Field(min_length=3) — 2 items must fail."""
        data = _minimal_review_data()
        data["weaknesses"] = ["one", "two"]
        with pytest.raises(ValidationError):
            ResumeReviewResponse(**data)

    def test_bullet_transformations_rejects_fewer_than_3(self):
        """bullet_transformations has Field(min_length=3) — 2 items must fail."""
        data = _minimal_review_data()
        data["bullet_transformations"] = [
            {"original": "a", "critique": "b", "improved": "c"},
            {"original": "d", "critique": "e", "improved": "f"},
        ]
        with pytest.raises(ValidationError):
            ResumeReviewResponse(**data)


# ═══════════════════════════════════════════════════════════════════════════
# ResumeImprovementResponse
# ═══════════════════════════════════════════════════════════════════════════

class TestResumeImprovementResponse:
    """Tests for the improvement response schema."""

    def test_valid_response_passes(self, sample_improvement_response):
        """A fully valid improvement response should pass validation."""
        assert sample_improvement_response.improved_summary is not None
        assert len(sample_improvement_response.improved_bullets) > 0

    def test_target_role_accepts_none(self):
        """target_role is Optional — None must be accepted."""
        response = ResumeImprovementResponse(
            target_role=None,
            improved_summary="Test summary",
            improved_bullets=[],
            skills_improvements=SkillsImprovement(
                current_skills=["Python"], recommendations=["Add more"],
            ),
            ats_keyword_suggestions=ATSKeywordSuggestions(
                keywords=["Python"], recommendations=["Use full forms"],
            ),
        )
        assert response.target_role is None

    def test_target_role_accepts_string(self):
        """target_role accepts a non-None string value."""
        response = ResumeImprovementResponse(
            target_role="Backend Engineer",
            improved_summary="Test summary",
            improved_bullets=[],
            skills_improvements=SkillsImprovement(
                current_skills=["Python"], recommendations=["Add more"],
            ),
            ats_keyword_suggestions=ATSKeywordSuggestions(
                keywords=["Python"], recommendations=["Use full forms"],
            ),
        )
        assert response.target_role == "Backend Engineer"


# ═══════════════════════════════════════════════════════════════════════════
# ResumeAnalysisResponse — combined response
# ═══════════════════════════════════════════════════════════════════════════

class TestResumeAnalysisResponse:
    """Tests for the combined response wrapping review + improvements."""

    def test_combines_both_responses(
        self, sample_review_response, sample_improvement_response
    ):
        """ResumeAnalysisResponse should wrap both sub-responses correctly."""
        combined = ResumeAnalysisResponse(
            review=sample_review_response,
            improvements=sample_improvement_response,
        )
        assert combined.review.overall_score == 72
        assert combined.improvements.improved_summary is not None


# ═══════════════════════════════════════════════════════════════════════════
# Helper
# ═══════════════════════════════════════════════════════════════════════════

def _minimal_review_data():
    """
    Returns a dict of valid review data that can be selectively broken
    to test individual Field constraints.
    """
    return {
        "overall_score": 70,
        "category_scores": {
            "ATS_structure": 18,
            "impact_and_metrics": 20,
            "language_and_brevity": 14,
            "skills_and_keywords": 18,
        },
        "executive_summary": "Solid resume with room for improvement.",
        "strengths": ["Good structure", "Quantified achievements", "Clear formatting"],
        "weaknesses": ["Missing summary", "Weak bullets", "No skill categories"],
        "ATS_compatibility_suggestions": {
            "parsing_safety": "Use single-column layout",
            "keyword_optimization_strategy": "Include acronyms and full forms",
        },
        "prioritized_action_plan": {
            "P0": "Fix formatting",
            "P1": "Rewrite bullets",
            "P2": "Polish language",
        },
        "bullet_transformations": [
            {"original": "Did stuff", "critique": "Vague", "improved": "Built X using Y"},
            {"original": "Worked on things", "critique": "No impact", "improved": "Developed A for B"},
            {"original": "Helped team", "critique": "Passive", "improved": "Led team of 5"},
        ],
        "hiring_readiness": "Good",
        "section_analysis": [
            {
                "section": "Experience",
                "present": True,
                "strengths": ["Has entries"],
                "weaknesses": ["Weak bullets"],
                "recommendations": ["Improve bullets"],
            },
        ],
    }
