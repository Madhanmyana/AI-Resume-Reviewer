import { useState } from "react";
import Navbar from "./components/Navbar";
import UploadSection from "./components/UploadSection";
import LoadingScreen from "./components/LoadingScreen";
import Dashboard from "./components/Dashboard";
import { analyzeResume } from "./api/resumeApi";
import type { AnalysisResponse } from "./types";

const messages = [
  "Parsing your PDF…",
  "Checking ATS structure…",
  "Evaluating impact and metrics…",
  "Matching keywords to the target role…",
];

export default function App() {
  const [data, setData] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(messages[0]);
  const [toast, setToast] = useState("");

  const analyze = async (f: File, r: string) => {
    setData(null);
    setLoading(true);
    let i = 0;
    const timer = window.setInterval(() => {
      i = (i + 1) % messages.length;
      setMessage(messages[i]);
    }, 520);
    try {
      const result = await analyzeResume(f, r);
      setData(result);
      requestAnimationFrame(() =>
        document.getElementById("review")?.scrollIntoView({ behavior: "smooth" })
      );
    } catch (err) {
      setToast(err instanceof Error ? err.message : "Analysis failed");
      window.setTimeout(() => setToast(""), 4000);
    } finally {
      window.clearInterval(timer);
      setLoading(false);
    }
  };

  const copied = () => {
    setToast("Copied");
    window.setTimeout(() => setToast(""), 1400);
  };

  return (
    <div className="app">
      <Navbar
        showNewReview={!!data}
        onNewReview={() => {
          setData(null);
          setLoading(false);
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />
      <main className="shell">
        <section className="page-title">
          <div>
            <div className="eyebrow">AI-assisted resume analysis</div>
            <h1>Make your resume harder to ignore.</h1>
          </div>
          {data?.improvements.target_role && (
            <span className="status-badge">{data.improvements.target_role}</span>
          )}
        </section>

        {!data && !loading && <UploadSection onAnalyze={analyze} />}
        {loading && <LoadingScreen message={message} />}
        {data && (
          <>
            <Dashboard data={data} onCopied={copied} />
            <footer className="footer">
              <span>AI Resume Reviewer · Analysis preview</span>
              <button
                className="button button-outline"
                onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              >
                Back to top ↑
              </button>
            </footer>
          </>
        )}
      </main>
      <div className={`toast ${toast ? "show" : ""}`} aria-live="polite">
        {toast}
      </div>
    </div>
  );
}
