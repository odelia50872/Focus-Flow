import { useCallback, useEffect, useRef, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";
import { Camera } from "../components/Camera";
import { ContentViewer } from "../components/ContentViewer";
import { FocusAlert } from "../components/FocusAlert";
import { MODEL_OPTIONS } from "../utils/focusInference";

export function Session() {
  const { contentId = "" } = useParams();
  const { token, user, loading } = useAuth();
  const [session, setSession] = useState(null);
  const [youtubeId, setYoutubeId] = useState(null);
  const [contentTitle, setContentTitle] = useState("");
  const [lastScore, setLastScore] = useState(null);
  const [error, setError] = useState(null);
  const [ended, setEnded] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [selectedModel, setSelectedModel] = useState("v4_2");
  const [showAlert, setShowAlert] = useState(false);
  const startedAt = useRef(Date.now());
  const posting = useRef(false);
  const playerRef = useRef(null);
  const lowFocusCount = useRef(0);

  useEffect(() => {
    if (!token || !contentId) return;
    let cancelled = false;

    async function boot() {
      try {
        const items = await api.listContent(token);
        const content = items.find((i) => i.id === contentId);
        if (!content) throw new Error("Content not found in your library");

        const match = content.source.match(
          /(?:youtube\.com\/watch\?v=|youtu\.be\/|^)([A-Za-z0-9_-]{11})/,
        );
        const ytId = match ? match[1] : content.source;

        const s = await api.startSession(token, contentId);
        if (cancelled) return;
        setYoutubeId(ytId);
        setContentTitle(content.title);
        setSession(s);
        startedAt.current = Date.now();
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : "Could not start session");
      }
    }

    boot();
    return () => { cancelled = true; };
  }, [token, contentId]);

  const onScore = useCallback(
    async (score, meta) => {
      if (!token || !session || ended || posting.current) return;
      posting.current = true;
      setLastScore(score);

      // show alert after 2 consecutive low scores
      if (score < 0.4) {
        lowFocusCount.current += 1;
        if (lowFocusCount.current >= 2) setShowAlert(true);
      } else {
        lowFocusCount.current = 0;
      }

      try {
        const position = (Date.now() - startedAt.current) / 1000;
        await api.postReading(token, session.id, {
          position,
          score,
          model_name: meta.modelName,
          extraction_type: meta.extractionType,
        });
        setSession((prev) =>
          prev
            ? {
                ...prev,
                average_score:
                  prev.average_score === null
                    ? score
                    : (prev.average_score * prev.reading_count + score) / (prev.reading_count + 1),
                reading_count: prev.reading_count + 1,
              }
            : prev,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to save focus sample");
      } finally {
        posting.current = false;
      }
    },
    [token, session, ended],
  );

  function handleRewind() {
    if (playerRef.current) playerRef.current.rewind(30);
    setShowAlert(false);
    lowFocusCount.current = 0;
  }

  function handleDismissAlert() {
    setShowAlert(false);
    lowFocusCount.current = 0;
  }

  async function endSession() {
    if (!token || !session) return;
    try {
      const res = await api.endSession(token, session.id);
      setSession(res);
      setEnded(true);
      setCameraEnabled(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not end session");
    }
  }

  if (loading) return <main className="page">Loading…</main>;
  if (!user || !token) return <Navigate to="/login" replace />;

  const avgScore = session?.average_score ?? null;

  return (
    <main className="page session-page">
      <div className="session-top">
        <Link to="/library">← Back to library</Link>
        <div className="scoreboard">
          <span>Last: {lastScore === null ? "—" : `${Math.round(lastScore * 100)}%`}</span>
          <span>Average: {avgScore === null ? "—" : `${Math.round(avgScore * 100)}%`}</span>

          {!ended && session && !cameraEnabled && (
            <div className="model-select-row">
              <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
                {MODEL_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
              <button type="button" onClick={() => setCameraEnabled(true)}>
                Enable camera
              </button>
            </div>
          )}

          {!ended && session && (
            <button type="button" onClick={endSession}>
              End session
            </button>
          )}
          {ended && <span className="ok">Session ended ✓</span>}
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {!session && !error && <p className="muted">Starting session…</p>}

      {session && youtubeId && (
        <div className="session-grid">
          <ContentViewer youtubeId={youtubeId} title={contentTitle} ref={playerRef} />
          <Camera enabled={cameraEnabled && !ended} model={selectedModel} onScore={onScore} />
        </div>
      )}

      {!cameraEnabled && session && !ended && (
        <p className="muted" style={{ marginTop: "0.75rem" }}>
          Select a model and click "Enable camera" to start measuring focus. Only numeric scores are
          sent to the server — video never leaves your browser.
        </p>
      )}

      {showAlert && !ended && (
        <FocusAlert
          score={lastScore}
          onDismiss={handleDismissAlert}
          onRewind={handleRewind}
        />
      )}
    </main>
  );
}
