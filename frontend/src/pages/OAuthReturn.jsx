import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function OAuthReturn() {
  const navigate = useNavigate();

  useEffect(() => {
    // When user returns from Google OAuth successfully
    localStorage.setItem("isLoggedIn", "true");
    navigate("/");
  }, [navigate]);

  return <p>Signing you in...</p>;
}
