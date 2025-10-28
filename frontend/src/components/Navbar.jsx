import { NavLink } from "react-router-dom";

const linkStyle = ({ isActive }) => ({
  textDecoration: "none",
  padding: "0.5rem 0.75rem",
  fontWeight: isActive ? 700 : 500,
});

export default function Navbar() {
  return (
    <nav className="nav">
      <div className="brand">CrowdLib</div>
      <div className="links">
        <NavLink to="/" style={linkStyle} end>Home</NavLink>
        <NavLink to="/explore" style={linkStyle}>Explore</NavLink>
        <NavLink to="/create" style={linkStyle}>Create</NavLink>
        <NavLink to="/profile" style={linkStyle}>Profile</NavLink>
        <NavLink to="/login" style={linkStyle}>Login</NavLink>
        <NavLink to="/signup" style={linkStyle}>Sign Up</NavLink>
      </div>
    </nav>
  );
}
