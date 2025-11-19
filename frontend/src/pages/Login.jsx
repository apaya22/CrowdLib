import { Link } from "react-router-dom";
export const BACKEND = "http://localhost:8000";     // use the SAME host you used in Django & Google
export const FRONTEND = window.location.origin;     // e.g., http://localhost:5173

export function startGoogleOAuth(nextPath = "/oauth-return") {
  const nextUrl = new URL(nextPath, FRONTEND).toString();
  const url = `${BACKEND}/auth/login/google-oauth2/?next=${encodeURIComponent(nextUrl)}`;
  window.location.assign(url);
}

export default function Login() {
  return (
    <div className="auth auth--center">
      <section className="auth-card" role="region" aria-labelledby="login-title">
        <div className="auth-header">
          <h1 id="login-title" className="auth-title">Sign in to Crowdlib</h1>
          <p className="auth-subtitle">Log in with Google to continue</p>
        </div>

        {/* Google OAuth here */}
        <button className="btn btn--oauth" type="button" aria-label="Sign in with Google" onClick={() => startGoogleOAuth("/oauth-return")}>
          <GoogleIcon />
          <span>Continue with Google</span>
        </button>
        <p className="auth-caption">
          You’ll be redirected to Google to securely sign in.
        </p>
      </section>
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
