import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API = "http://127.0.0.1:8000/api/users/";

export default function Signup() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    //Passsword check
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      //backend requires: username, email, oauth_provider, oauth_id
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

      // Some backends return empty body on 201; guard against JSON parse errors
      // let data = {};
      // try { data = await res.json(); } catch (_) {}
      const raw = await res.text();
      let data; try { data = JSON.parse(raw); } catch { data = { error: raw }; }

      if (!res.ok) {
        // Show backend error if available
        setError(
          data?.error ||
          (res.status === 400 ? "Invalid signup data" : "Signup failed")
        );
        return;
      }

      // Success (201 created) -> go home
      navigate("/");

    } catch {
      setError("Network error. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-wrap">
      <section className="auth-card">
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Join CrowdLib in seconds.</p>

        <form onSubmit={onSubmit} className="auth-form">
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
    </main>
  );
}
