import type { AnalysisResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeResume(file: File, targetRole: string): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("resume", file);

  const url = targetRole
    ? `${API_BASE_URL}/review-resume?target_role=${encodeURIComponent(targetRole)}`
    : `${API_BASE_URL}/review-resume`;

  const response = await fetch(url, { method: "POST", body: formData });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail ?? "Resume analysis failed");
  }

  return response.json();
}
