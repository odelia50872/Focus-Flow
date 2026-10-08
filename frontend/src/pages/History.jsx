import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";

export function History() {
  const { token, user, loading } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;
    api
      .listSessions(token)
      .then(setSessions)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history"));
  }, [token]);

  if (loading) return <main className="page">Loading…</main>;
  if (!user || !token) return <Navigate to="/login" replace />;

  return (
    <main className="page">
      <h1>History</h1>
      <p className="muted">Past focus sessions for your account only.</p>
      {error && <p className="error">{error}</p>}
      <ul className="history-list">
        {sessions.map((s) => (
          <li key={s.id}>
            <div>
              <strong>{s.content_title || `Session ${s.id}`}</strong>
              <div className="muted">
                {s.ended_at ? "Completed" : "In progress"} · {s.reading_count} readings · focus{" "}
                {s.average_score === null ? "n/a" : `${Math.round(s.average_score * 100)}%`}
              </div>
              <div className="muted" style={{ fontSize: "0.82rem" }}>
                {new Date(s.started_at).toLocaleString()}
              </div>
            </div>
            <Link className="button-link" to={`/session/${s.content_id}`}>
              Watch again
            </Link>
          </li>
        ))}
        {sessions.length === 0 && <li className="muted">No sessions yet.</li>}
      </ul>
    </main>
  );
}
