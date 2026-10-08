import { Navigate, Route, Routes } from "react-router-dom";
import { Header } from "./components/Header";
import { useAuth } from "./auth";
import { History } from "./pages/History";
import { Library } from "./pages/Library";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Session } from "./pages/Session";

export default function App() {
  const { user, loading } = useAuth();

  return (
    <div className="app-shell">
      <Header />
      {loading ? (
        <main className="page">Loading…</main>
      ) : (
        <Routes>
          <Route path="/" element={<Navigate to={user ? "/library" : "/login"} replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/library" element={<Library />} />
          <Route path="/session/:contentId" element={<Session />} />
          <Route path="/history" element={<History />} />
        </Routes>
      )}
    </div>
  );
}
