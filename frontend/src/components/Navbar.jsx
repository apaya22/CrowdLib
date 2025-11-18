import { NavLink } from "react-router-dom";
import { useState, useEffect } from "react";

const API_ROOT = "http://localhost:8000/api";

const linkStyle = ({ isActive }) => ({
  textDecoration: "none",
  padding: "0.5rem 0.75rem",
  fontWeight: isActive ? 700 : 500,
});

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    async function checkLogin() {
      try {
        const res = await fetch(`${API_ROOT}/users/profile/`, {
          credentials: "include",
        });

    fetch(`${API_BASE}/api/users/profile/`, {
      credentials: "include",
    })
      .then((res) => {
        console.log("Profile response:", res.status); // DEBUG
        if (res.status === 200) {
          setIsLoggedIn(true);
        } else {
          setIsLoggedIn(false);
        }
      })
      .catch((err) => {
        console.log("Profile fetch error:", err);
        setIsLoggedIn(false);
      }
    }

    checkLogin();
  }, []);

  // Logout Handler
  const handleLogout = async () => {
    const csrf = getCookie("csrftoken");
    console.log("CSRF token:", csrf);
    console.log("All cookies:", document.cookie);

    try {
      const res = await fetch(`${API_ROOT}/users/logout/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(csrf ? { "X-CSRFToken": csrf } : {}),
        },
      });
  }, []);

  const handleLogout = () => {
    fetch(`${API_BASE}/api/logout/`, {
      method: "POST",
      credentials: "include",
    })
      .then(() => {
        console.log("Logged out.");
        setIsLoggedIn(false);
        window.location.href = "/";
      } else {
        const errorData = await res.json().catch(() => ({}));
        console.error("Logout failed:", res.status, errorData);
        alert(`Logout failed: ${errorData.detail || errorData.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error("Logout error:", err);
      alert("Network error during logout");
    }
  };

  return (
    <nav className="nav">
      <div className="brand">CrowdLib</div>

      <div className="links">
        <NavLink to="/" style={linkStyle} end>Home</NavLink>
        <NavLink to="/explore" style={linkStyle}>Explore</NavLink>
        <NavLink to="/create" style={linkStyle}>Create</NavLink>
        <NavLink to="/profile" style={linkStyle}>Profile</NavLink>

        {isLoggedIn ? (
          <span
    onClick={handleLogout}
    style={{
      ...linkStyle({ isActive: false }),
      cursor: "pointer",
      color: "#663399" // same purple
    }}
  >
          Logout
        </span>
        ) : (
          <NavLink to="/login" style={linkStyle}>Login</NavLink>
        )}
      </div>
    </nav>
  );
}
