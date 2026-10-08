import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth";

export function Library() {
  const { token, user, loading } = useAuth();
  const [items, setItems] = useState([]);
  const [error, setError] = useState(null);
  const [title, setTitle] = useState("");
  const [source, setSource] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!token) return;
    api
      .listContent(token)
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, [token]);

  if (loading) return <main className="page">Loading…</main>;
  if (!user || !token) return <Navigate to="/login" replace />;

  async function onAdd(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const created = await api.createContent(token, {
        title: title.trim(),
        type: "youtube",
        source: source.trim(),
      });
      setItems((prev) => [created, ...prev]);
      setTitle("");
      setSource("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add video");
    } finally {
      setBusy(false);
    }
  }

  async function onDelete(id) {
    if (!confirm("Delete this item?")) return;
    try {
      await api.deleteContent(token, id);
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete");
    }
  }

  return (
    <main className="page">
      <h1>Library</h1>
      <p className="muted">Add a YouTube video and start a focus session.</p>

      <form className="add-form" onSubmit={onAdd}>
        <label>
          Title
          <input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </label>
        <label>
          YouTube URL or ID
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="https://youtube.com/watch?v=... or video ID"
            required
          />
        </label>
        <button type="submit" disabled={busy}>
          {busy ? "Adding…" : "Add video"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <ul className="video-list">
        {items.map((item) => (
          <li key={item.id}>
            <div>
              <strong>{item.title}</strong>
              <div className="muted">{item.source}</div>
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Link className="button-link" to={`/session/${item.id}`}>
                Start session
              </Link>
              <button
                type="button"
                onClick={() => onDelete(item.id)}
                style={{ background: "var(--danger)", color: "#fff" }}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
        {items.length === 0 && <li className="muted">No videos yet — add one above.</li>}
      </ul>
    </main>
  );
}
