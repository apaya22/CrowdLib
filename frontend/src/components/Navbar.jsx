import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";

const linkStyle = ({ isActive }) => ({
  textDecoration: "none",
  padding: "1.5rem 0.75rem",
  fontWeight: isActive ? 700 : 500,
});

const API_BASE = "http://127.0.0.1:8000";

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/users/profile/`, {
credentials: "include",})
      .then((res) => {
        setIsLoggedIn(res.ok);
      })
      .catch(() => {
        setIsLoggedIn(false);
      });
  }, []);

  function handleLogout() {
    window.location.href = "/";
  }

  return (
    <nav className="nav">
      <div className="brand">CrowdLib</div>
      <div className="links">
        <NavLink to="/" style={linkStyle} end>Home</NavLink>
        <NavLink to="/explore" style={linkStyle}>Explore</NavLink>
        <NavLink to="/create" style={linkStyle}>Create</NavLink>
        <NavLink to="/profile" style={linkStyle}>Profile</NavLink>

        {localStorage.getItem("isLoggedIn") === "true" ? (
  <NavLink to="/" style={linkStyle} onClick={() => {
    localStorage.removeItem("isLoggedIn");
  }}>
    Logout
  </NavLink>
) : (
  <>
            <NavLink to="/login" style={linkStyle}>Login</NavLink>
          </>
)}
      </div>
    </nav>
  );
}

