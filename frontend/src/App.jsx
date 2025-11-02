import { Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Explore from "./pages/Explore.jsx";
import Create from "./pages/Create.jsx";
import Profile from "./pages/Profile.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import MadlibPlay from "./pages/MadlibPlay.jsx";
import "./App.css";

const linkStyle = ({ isActive }) => ({
  textDecoration: "none",
  padding: "0.5rem 0.75rem",
  fontWeight: isActive ? 700 : 500,
});

export default function App() {
  return (
    <div className="app">
      <nav className="nav">
        <div className="brand">CrowdLib</div>
        <div className="links">
          <NavLink to="/" style={linkStyle} end>Home</NavLink>
          <NavLink to="/explore" style={linkStyle}>Explore</NavLink>
          <NavLink to="/create" style={linkStyle}>Create</NavLink>
          <NavLink to="/profile" style={linkStyle}>Profile</NavLink>
          <NavLink to="/login" style={linkStyle}>Login</NavLink>
        </div>
      </nav>

      <main className="container">
        <Routes>
          <Route index element={<Home />} />
          <Route path="explore" element={<Explore />} />
          <Route path="create" element={<Create />} />
          <Route path="profile" element={<Profile />} />
          <Route path="login" element={<Login />} />
          <Route path="signup" element={<Signup />} />
          <Route path="madlibs/:id" element={<MadlibPlay />} />
        </Routes>
      </main>
    </div>
  );
}
