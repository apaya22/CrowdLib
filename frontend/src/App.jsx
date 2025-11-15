import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Explore from "./pages/Explore.jsx";
import Create from "./pages/Create.jsx";
import Profile from "./pages/Profile.jsx";
import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";
import MadlibPlay from "./pages/MadlibPlay.jsx";
import OAuthReturn from "./pages/OAuthReturn.jsx";
import Navbar from "./components/Navbar.jsx";
import Comment from "./pages/Comment.jsx";
import "./App.css";

export default function App() {
  return (
    <div className="app">
      <Navbar />

      <main className="container">
        <Routes>
          <Route index element={<Home />} />
          <Route path="explore" element={<Explore />} />
          <Route path="create" element={<Create />} />
          <Route path="profile" element={<Profile />} />
          <Route path="login" element={<Login />} />
          <Route path="signup" element={<Signup />} />
          <Route path="madlibs/:id" element={<MadlibPlay />} />
          <Route path="/oauth-return" element={<OAuthReturn />} />
          <Route path="/madlibs/:id/comments" element={<Comment />} />
        </Routes>
      </main>
    </div>
  );
}
