from pydantic import BaseModel

class ImprovedBullet(BaseModel):
    original:str
    improved:str
    reason:str

class SkillsImprovement(BaseModel):
    current_skills: list[str]
    recommendations: list[str]

class ATSKeywordSuggestions(BaseModel):
    keywords: list[str]
    recommendations: list[str]

class ResumeImprovementResponse(BaseModel):
    target_role: str | None = None
    improved_summary: str
    improved_bullets: list[ImprovedBullet]
    skills_improvements: SkillsImprovement
    ats_keyword_suggestions: ATSKeywordSuggestions