export default function Navbar({ onNewReview, showNewReview }: { onNewReview: () => void; showNewReview?: boolean }) {
  return (
    <header className="navbar">
      <div className="brand">Resume Reviewer</div>
      <div style={{ flex: 1 }}></div>
      {showNewReview && (
        <button className="button button-outline" onClick={onNewReview}>
          New Review
        </button>
      )}
    </header>
  );
}
