// frontend/src/pages/OAuthCompleteSignup.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = "http://127.0.0.1:8000"; // your backend

function getCookie(name) {
  const m = document.cookie.match(`\\b${name}=([^;]*)\\b`);
  return m ? decodeURIComponent(m[1]) : null;
}

export default function OAuthCompleteSignup() {
  const [msg, setMsg] = useState("Finalizing sign up…");
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        // 1) Read OAuth data (you already expose this)
        const whoRes = await fetch(`${API_BASE}/api/debug/oauth/`, {
          credentials: "include",          // include session cookie
        });

        if (whoRes.status === 401) {
          setMsg("Not authenticated with Google. Please try again.");
          return;
        }
        if (!whoRes.ok) {
          setMsg("Could not read OAuth data.");
          return;
        }

        const who = await whoRes.json();
        const dj = who.django_user || {};
        const google = (who.social_auth || []).find(
          s => s.provider === "google-oauth2" || s.provider === "google"
        );

        if (!dj.email || !google?.uid) {
          setMsg("Missing Google account info from backend.");
          return;
        }

        // 2) Build payload for your POST /api/users/
        const payload = {
          username: dj.username || dj.email.split("@")[0],
          email: dj.email,
          oauth_provider: google.provider || "google-oauth2",
          oauth_id: google.uid,
          profile_picture: google.extra_data?.picture || undefined,
          bio: ""
        };

        // 3) Create the user in Mongo via your ViewSet
        const res = await fetch(`${API_BASE}/api/users/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
            // If SessionAuthentication + CSRF is enabled, send CSRF token:
            "X-CSRFToken": getCookie("csrftoken") || "",
          },
          body: JSON.stringify(payload),
        });

        // Try to parse JSON, but guard against empty body
        let data = {};
        try { data = await res.json(); } catch {}

        if (!res.ok) {
          // If the user already exists, just proceed
          if (res.status === 400 && typeof data?.error === "string" &&
              /already exists|duplicate/i.test(data.error)) {
            navigate("/", { replace: true });
            return;
          }
          setMsg(data?.error || "Signup failed.");
          return;
        }

        // 4) Success
        navigate("/", { replace: true });
      } catch (e) {
        setMsg("Something went wrong finishing Google sign up.");
      }
    })();
  }, [navigate]);

  return <p style={{ margin: "2rem" }}>{msg}</p>;
}
