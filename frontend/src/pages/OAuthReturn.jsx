// frontend/src/pages/OAuthReturn.jsx
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function OAuthReturn() {
  const navigate = useNavigate();

  useEffect(() => {
    // Google OAuth + backend session succeeded
    localStorage.setItem("isLoggedIn", "true");

    // Redirect user to homepage
    navigate("/");
  }, [navigate]);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Signing you in…</h2>
    </div>
  );
}
