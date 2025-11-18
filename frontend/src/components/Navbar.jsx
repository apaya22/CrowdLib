import { NavLink } from "react-router-dom";
import { useState, useEffect } from "react";

const API_ROOT = "http://localhost:8000/api";

function getCookie(name) {
  const cookieString = document.cookie;
  const cookies = cookieString.split("; ");

  for (let cookie of cookies) {
    const [key, val] = cookie.split("=");
    if (key === name) return decodeURIComponent(val);
  }
  return null;
}

export default function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check Login Status
  useEffect(() => {
    async function checkLogin() {
      try {
        const res = await fetch(`${API_ROOT}/users/profile/`, {
          credentials: "include",
        });

        console.log("Profile response:", res.status);
        setIsLoggedIn(res.ok); // 200 → logged in
      } catch (err) {
        console.error("Profile fetch error:", err);
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

      console.log("Logout response:", res.status);

      if (res.ok) {
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

  const linkStyle = ({ isActive }) => ({
    marginLeft: "20px",
    textDecoration: "none",
    color: isActive ? "#663399" : "black",
    fontWeight: isActive ? "bold" : "normal",
  });

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
              color: "#663399",
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
