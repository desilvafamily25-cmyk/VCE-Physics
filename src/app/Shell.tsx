import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { useTheme } from "../lib/useTheme";
import { OrbitIcon } from "../auth/AuthGate";

export function Shell() {
  const { user, signOut } = useAuth();
  const { theme, toggle } = useTheme();

  const link = ({ isActive }: { isActive: boolean }) => (isActive ? "shell-link shell-link-active" : "shell-link");

  return (
    <div className="shell">
      <nav className="shell-nav" aria-label="Main navigation">
        <span className="brand-mark shell-brand">
          <OrbitIcon />
          <span>VCE Physics 50</span>
        </span>
        <NavLink to="/dashboard" className={link}>
          <span className="link-text">Dashboard</span>
        </NavLink>
        <NavLink to="/papers" className={link}>
          <span className="link-text">Past Papers</span>
        </NavLink>
        <NavLink to="/topics" className={link}>
          <span className="link-text">Practice by Topic</span>
        </NavLink>
        <NavLink to="/errors" className={link}>
          <span className="link-text">My Errors</span>
        </NavLink>
        <NavLink to="/progress" className={link}>
          <span className="link-text">Progress</span>
        </NavLink>
        <span className="shell-spacer" />
        <button
          type="button"
          className="theme-toggle"
          onClick={toggle}
          title={`Theme: ${theme}`}
          aria-label="Toggle light/dark theme"
        >
          {theme === "dark" ? <MoonIcon /> : theme === "light" ? <SunIcon /> : <AutoIcon />}
        </button>
        {user && (
          <span className="shell-account">
            <span className="shell-account-email">{user.email}</span>
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => void signOut()}>
              Sign out
            </button>
          </span>
        )}
      </nav>
      <Outlet />
    </div>
  );
}

function SunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 1020.354 15.354z" />
    </svg>
  );
}

function AutoIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="4" width="18" height="14" rx="2" />
      <path d="M8 20h8M12 18v2" />
    </svg>
  );
}
