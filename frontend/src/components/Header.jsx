import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../auth";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="site-header">
      <Link to="/" className="brand">
        FocusFlow
      </Link>
      {user && (
        <nav className="nav">
          <NavLink to="/library">Library</NavLink>
          <NavLink to="/history">History</NavLink>
          <button type="button" className="linkish" onClick={logout}>
            Log out ({user.display_name})
          </button>
        </nav>
      )}
    </header>
  );
}
