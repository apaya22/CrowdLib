import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export const BACKEND = (
  import.meta.env.VITE_API_BASE || "http://localhost:8000/api"
).replace(/\/$/, "");

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    async function loadProfile() {
      try {
        setLoading(true);
        setError("");

        const res = await fetch(`${BACKEND}/users/profile/`, {
          method: "GET",
          credentials: "include",
        });

        if (res.status === 401 || res.status === 403) {
          // not logged in, send to login
          navigate("/login", { replace: true, state: { from: "/profile" } });
          return;
        }

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const json = await res.json();
        if (!cancelled) setUser(json);
      } catch (err) {
        if (!cancelled) setError(err.message || "Failed to load profile");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadProfile();
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  const formattedDate =
    user?.created_at ? new Date(user.created_at).toLocaleDateString() : "";

  return (
    <div className="container profile-page">
      <h1 className="profile-page__title">Profile</h1>

      {loading && <p className="muted">Loading your profile…</p>}

      {error && !loading && (
        <div className="card profile-error">
          <p>Couldn’t load your profile.</p>
          <code>{error}</code>
        </div>
      )}

      {!loading && user && (
        <section className="card profile-card">
          <div className="profile-header">
            <div className="profile-header__text">
              <h2 className="profile-username">{user.username}</h2>
              <p className="profile-email">{user.email}</p>
              <p className="profile-meta">
                Signed in with <strong>{user.oauth_provider}</strong>
                {formattedDate && <> · Member since {formattedDate}</>}
              </p>
            </div>
          </div>

          <div className="profile-body">
            <div className="profile-stats">
              <div className="profile-stat">
                <span className="profile-stat__label">Followers</span>
                <span className="profile-stat__value">
                  {user.followers_count ?? 0}
                </span>
              </div>
              <div className="profile-stat">
                <span className="profile-stat__label">Following</span>
                <span className="profile-stat__value">
                  {user.following_count ?? 0}
                </span>
              </div>
              <div className="profile-stat">
                <span className="profile-stat__label">Visibility</span>
                <span className="profile-stat__value">
                  {user.public ? "Public" : "Private"}
                </span>
              </div>
            </div>

            <div className="profile-bio">
              <h3>Bio</h3>
              <p className={user.bio ? "" : "muted"}>
                {user.bio || "You haven’t added a bio yet."}
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default Profile;
