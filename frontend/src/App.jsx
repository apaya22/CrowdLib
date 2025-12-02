import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Explore from "./pages/Explore.jsx";
import Create from "./pages/Create.jsx";
import Profile from "./pages/Profile.jsx";
import Login from "./pages/Login.jsx";
import MadlibPlay from "./pages/MadlibPlay.jsx";
import Navbar from "./components/Navbar.jsx";
import Comment from "./pages/Comment.jsx";
import Posts from "./pages/Posts.jsx";
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
          <Route path="madlibs/:id" element={<MadlibPlay />} />          
          <Route path="/madlibs/:id/comments" element={<Comment />} />
          <Route path="filled-madlibs/:id/comment" element={<Comment />} />
          <Route path="posts" element={<Posts />} />
        </Routes>
      </main>
    </div>
  );
}
