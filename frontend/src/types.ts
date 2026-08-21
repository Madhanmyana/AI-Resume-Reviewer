export interface CategoryScores {
  ATS_structure: number;
  impact_and_metrics: number;
  language_and_brevity: number;
  skills_and_keywords: number;
}

export interface BulletTransformation {
  original: string;
  critique: string;
  improved: string;
}

export interface ATSSuggestions {
  parsing_safety: string;
  keyword_optimization_strategy: string;
}

export interface PrioritizedActionPlan {
  P0: string;
  P1: string;
  P2: string;
}

export interface SectionAnalysis {
  section: string;
  present: boolean;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface ResumeReview {
  overall_score: number;
  category_scores: CategoryScores;
  executive_summary: string;
  strengths: string[];
  weaknesses: string[];
  ATS_compatibility_suggestions: ATSSuggestions;
  prioritized_action_plan: PrioritizedActionPlan;
  bullet_transformations: BulletTransformation[];
  hiring_readiness: string;
  section_analysis: SectionAnalysis[];
}

export interface ImprovedBullet {
  original: string;
  improved: string;
  reason: string;
}

export interface SkillsImprovement {
  current_skills: string[];
  recommendations: string[];
}

export interface ATSKeywordSuggestions {
  keywords: string[];
  recommendations: string[];
}

export interface ResumeImprovement {
  target_role: string | null;
  improved_summary: string;
  improved_bullets: ImprovedBullet[];
  skills_improvements: SkillsImprovement;
  ats_keyword_suggestions: ATSKeywordSuggestions;
}

export interface AnalysisResponse {
  review: ResumeReview;
  improvements: ResumeImprovement;
}
