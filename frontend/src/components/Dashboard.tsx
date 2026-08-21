import type { AnalysisResponse } from "../types";

function CopyButton({
  text,
  onCopied,
  label,
}: {
  text: string;
  onCopied: () => void;
  label: string;
}) {
  return (
    <button
      className="mini-button"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
        } finally {
          onCopied();
        }
      }}
    >
      {label}
    </button>
  );
}

const List = ({ eyebrow, items }: { eyebrow: string; items: string[] }) => (
  <div className="dashboard-cell">
    <div className="eyebrow">{eyebrow}</div>
    <ul className="clean-list">
      {items.map((x) => (
        <li key={x}>{x}</li>
      ))}
    </ul>
  </div>
);

export default function Dashboard({
  data,
  onCopied,
}: {
  data: AnalysisResponse;
  onCopied: () => void;
}) {
  const { review, improvements } = data;

  const categoryScores = [
    { label: "ATS Structure", score: review.category_scores.ATS_structure, max: 25 },
    { label: "Impact & Metrics", score: review.category_scores.impact_and_metrics, max: 30 },
    { label: "Language & Brevity", score: review.category_scores.language_and_brevity, max: 20 },
    { label: "Skills & Keywords", score: review.category_scores.skills_and_keywords, max: 25 },
  ];

  const priorities = [
    { key: "P0", label: "Critical", text: review.prioritized_action_plan.P0 },
    { key: "P1", label: "Important", text: review.prioritized_action_plan.P1 },
    { key: "P2", label: "Polish", text: review.prioritized_action_plan.P2 },
  ];

  return (
    <section className="dashboard">

      {/* 01 — Score Overview */}
      <section id="review" className="score-overview">
        <div className="overall-score">
          <div className="eyebrow">Overall result</div>
          <div className="score-ring">
            <strong>{review.overall_score}</strong>
            <span>/ 100</span>
          </div>
          <span className="status-badge">{review.hiring_readiness}</span>
          <p>{review.executive_summary}</p>
        </div>
        <div className="category-scores">
          <div className="eyebrow">Category score breakdown</div>
          {categoryScores.map((c) => (
            <div className="score-row" key={c.label}>
              <span>{c.label}</span>
              <div className="score-bar">
                <span style={{ width: `${(c.score / c.max) * 100}%` }} />
              </div>
              <strong>
                {c.score}/{c.max}
              </strong>
            </div>
          ))}
        </div>
      </section>

      {/* 02 — Strengths, Weaknesses & ATS Tips */}
      <section className="section">
        <div className="section-head">
          <div>
            <div className="eyebrow">02 / Strengths & weaknesses</div>
            <h2>Keep the architecture. Strengthen the evidence.</h2>
          </div>
        </div>
        <div className="three-grid">
          <List eyebrow="Strengths" items={review.strengths} />
          <List eyebrow="Weaknesses" items={review.weaknesses} />
          <List
            eyebrow="ATS tips"
            items={[
              review.ATS_compatibility_suggestions.parsing_safety,
              review.ATS_compatibility_suggestions.keyword_optimization_strategy,
            ]}
          />
        </div>
      </section>

      {/* 03 — Priority Improvement Plan */}
      <section className="section">
        <div className="section-head">
          <div>
            <div className="eyebrow">03 / Priority improvement plan</div>
            <h2>Three passes, in this order.</h2>
          </div>
        </div>
        <div className="priority-list">
          {priorities.map((i) => (
            <div className="priority-row" key={i.key}>
              <div className={`priority-tag ${i.key.toLowerCase()}`}>
                {i.key} · {i.label}
              </div>
              <div style={{ gridColumn: "2 / -1" }}>
                <p>{i.text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 04 — Before → After (Improved Bullets) */}
      <section id="improvements" className="section">
        <div className="section-head">
          <div>
            <div className="eyebrow">04 / Before → after</div>
            <h2>Turn technical work into hiring evidence.</h2>
          </div>
        </div>
        {improvements.improved_bullets.map((i) => (
          <div className="improvement-row" key={i.original}>
            <div className="original-column">
              <div className="eyebrow">Original</div>
              <blockquote>{i.original}</blockquote>
            </div>
            <div className="improved-column">
              <div className="eyebrow">AI-improved</div>
              <div className="improved-text">{i.improved}</div>
              <CopyButton
                text={i.improved}
                onCopied={onCopied}
                label="Copy improvement"
              />
              <p className="reason">
                <strong>Reason:</strong> {i.reason}
              </p>
            </div>
          </div>
        ))}
      </section>

      {/* 05 — Professional Summary */}
      <section className="section">
        <div className="section-head">
          <div>
            <div className="eyebrow">05 / Professional summary</div>
            <h2>A tighter introduction for recruiters.</h2>
          </div>
        </div>
        <div
          className="summary-box"
          style={{ padding: "28px 34px 34px", borderTop: "1px solid var(--line)" }}
        >
          <div className="eyebrow">AI-improved summary</div>
          <p>{improvements.improved_summary}</p>
          <CopyButton
            text={improvements.improved_summary}
            onCopied={onCopied}
            label="Copy summary"
          />
        </div>
      </section>

      {/* 06 — Skills & ATS Keywords */}
      <section id="keywords" className="section">
        <div className="section-head">
          <div>
            <div className="eyebrow">06 / Skills & ATS keywords</div>
            <h2>Make the stack easier to scan.</h2>
          </div>
        </div>
        <div className="two-grid skills-grid">
          <div className="section-row">
            <div className="eyebrow">Detected skills</div>
            <div className="chips">
              {improvements.skills_improvements.current_skills.map((x) => (
                <span className="chip" key={x}>
                  {x}
                </span>
              ))}
            </div>
          </div>
          <div className="section-row">
            <div className="eyebrow">ATS keyword suggestions</div>
            <div className="chips">
              {improvements.ats_keyword_suggestions.keywords.map((x) => (
                <span className="chip chip-dark" key={x}>
                  {x}
                </span>
              ))}
            </div>
          </div>
          <List
            eyebrow="Skill recommendations"
            items={improvements.skills_improvements.recommendations}
          />
          <List
            eyebrow="Keyword recommendations"
            items={improvements.ats_keyword_suggestions.recommendations}
          />
        </div>
      </section>

      {/* 07 — Section-by-Section Analysis */}
      <section id="analysis" className="section">
        <div className="section-head">
          <div>
            <div className="eyebrow">07 / Section-by-section analysis</div>
            <h2>Every section has one clear next move.</h2>
          </div>
        </div>
        <div className="three-grid section-analysis-grid">
          {review.section_analysis.map((s) => (
            <div className="dashboard-cell" key={s.section}>
              <span className="section-status">
                {s.present ? "✓ Present" : "△ Missing"}
              </span>
              <h3>{s.section}</h3>
              {s.strengths.length > 0 && (
                <p>
                  <strong>Strengths: </strong>
                  {s.strengths.join(". ")}
                </p>
              )}
              {s.weaknesses.length > 0 && (
                <p>
                  <strong>Weaknesses: </strong>
                  {s.weaknesses.join(". ")}
                </p>
              )}
              {s.recommendations.length > 0 && (
                <div className="recommendation">
                  <strong>Recommendation: </strong>
                  {s.recommendations.join(". ")}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
