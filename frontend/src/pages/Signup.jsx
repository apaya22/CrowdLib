// frontend/src/pages/Signup.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
const BACKEND = "http://localhost:8000";     // <- define this
const API = `${BACKEND}/api/users/`;
const FRONTEND = window.location.origin; // http://localhost:5173

export function handleGoogleSignup(nextPath = "/oauth-return") {
  const nextUrl = new URL(nextPath, FRONTEND).toString();
  const url = `${BACKEND}/auth/login/google-oauth2/?next=${encodeURIComponent(nextUrl)}`;
  window.location.assign(url);
}

function AuthDivider({ label = "or" }) {
  return (
    <div className="auth-divider" role="separator" aria-label={label}>
      <span className="auth-divider__line" />
      <span className="auth-divider__label">{label}</span>
      <span className="auth-divider__line" />
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg
      className="g-icon"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 48 48"
      aria-hidden="true"
    >
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.8 32.7 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.6 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.2-.1-2.3-.4-3.5z" />
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 16 19 12 24 12c3.1 0 5.9 1.2 8 3.1l5.7-5.7C34.5 6.1 29.6 4 24 4 15.4 4 8.1 9.1 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 10-2 13.5-5.2l-6.2-5.2C29.3 36 26.8 37 24 37c-5.2 0-9.6-3.3-11.3-7.9l-6.6 5.1C8 38.9 15.4 44 24 44z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-1 2.9-3.4 5.2-6 6.5l6.2 5.2C38.2 37.6 44 32.9 44 24c0-1.2-.1-2.3-.4-3.5z" />
    </svg>
  );
}

export default function Signup() {
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      // This call only makes sense if your backend temporarily accepts local signups.
      const payload = {
        username: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        oauth_provider: "local",
        oauth_id: form.email.trim(),
      };

      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const raw = await res.text();
      let data; try { data = JSON.parse(raw); } catch { data = { error: raw }; }

      if (!res.ok) {
        setError(data?.error || (res.status === 400 ? "Invalid signup data" : "Signup failed"));
        return;
      }
      navigate("/");
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth auth--center">
      <section className="auth-card">
        <div className="auth-header">
          <h1 className="auth-title">Create your account</h1>
          <p className="auth-subtitle">Join CrowdLib in seconds.</p>
        </div>

        {/* Google OAuth here */}
        <button className="btn btn--oauth" type="button" aria-label="Sign un with Google" onClick={() => handleGoogleSignup("/")}>
          <GoogleIcon />
          <span>Continue with Google</span>
        </button>

        <AuthDivider label="or" />

        {/* (Optional) local form – can be hidden if you're only using Google */}
        <form onSubmit={onSubmit} className="auth-form" noValidate>
          <label className="field">
            <span className="auth-label">Name</span>
            <input
              className="auth-input"
              name="name"
              type="text"
              placeholder="Your name"
              value={form.name}
              onChange={onChange}
              required
            />
          </label>

          <label className="field">
            <span className="auth-label">Email</span>
            <input
              className="auth-input"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={onChange}
              required
            />
          </label>

          <label className="field">
            <span className="auth-label">Password</span>
            <input
              className="auth-input"
              name="password"
              type="password"
              placeholder="Create a password"
              value={form.password}
              onChange={onChange}
              required
            />
          </label>

          <label className="field">
            <span className="auth-label">Confirm password</span>
            <input
              className="auth-input"
              name="confirmPassword"
              type="password"
              placeholder="Re-enter password"
              value={form.confirmPassword}
              onChange={onChange}
              required
            />
          </label>

          {error && <div className="form-error">{error}</div>}

          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Create account"}
          </button>
        </form>

        <p className="auth-footnote">
          Already have an account? <a href="/login">Log in</a>
        </p>
      </section>
    </div>
  );
}