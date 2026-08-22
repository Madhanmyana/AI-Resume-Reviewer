from pydantic import BaseModel,Field
from enum import Enum

class HiringReadiness(str,Enum):
    Excellent="Excellent"
    Good="Good"
    Needs_Improvement="Needs Improvement"
    Not_Competitive_Yet="Not Competitive Yet"


class CategoryScores(BaseModel):
    ATS_structure:int=Field(...,ge=0,le=25)
    impact_and_metrics:int=Field(...,ge=0,le=30)
    language_and_brevity:int=Field(...,ge=0,le=20)
    skills_and_keywords:int=Field(...,ge=0,le=25)

class BulletTransformation(BaseModel):
    original:str
    critique:str
    improved:str

class ATSSuggestions(BaseModel):
    parsing_safety: str
    keyword_optimization_strategy: str

class PrioritizedActionPlan(BaseModel):
    P0: str
    P1: str
    P2: str

class SectionAnalysis(BaseModel):
    section: str
    present: bool
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]

class ResumeReviewResponse(BaseModel):
    overall_score:int=Field(...,ge=0,le=100)
    category_scores:CategoryScores
    executive_summary: str
    strengths:list[str]=Field(min_length=3,max_length=10)
    weaknesses:list[str]=Field(min_length=3,max_length=10)
    ATS_compatibility_suggestions: ATSSuggestions
    prioritized_action_plan: PrioritizedActionPlan
    bullet_transformations:list[BulletTransformation]=Field(min_length=3)
    hiring_readiness:HiringReadiness
    section_analysis: list[SectionAnalysis]