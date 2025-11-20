import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

const API_ROOT = "http://localhost:8000/api";

// helper to read csrftoken from cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

export default function Explore() {
  const mounted = useRef(true);

  const [madlibs, setMadlibs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");
  const [serverSearchOK, setServerSearchOK] = useState(true);

async function fetchMadlibs(q = "") {
  let url;

  if (q) {
    // When user hits Search button
    url = `${API_ROOT}/templates/search/?title=${encodeURIComponent(q)}`;
  } else {
    // Load all templates on page load
    url = `${API_ROOT}/templates/`;
  }

  const res = await fetch(url, {
    credentials: "include",
  });

  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status} :: ${txt.slice(0, 160)}`);
  }

  return res.json();
}


  useEffect(() => {
    mounted.current = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchMadlibs(query);
        if (!mounted.current) return;

        const items = Array.isArray(data)
          ? data
          : data.results ?? data.items ?? [];
        setMadlibs(items);
        setServerSearchOK(true);
      } catch (e) {
        if (query) {
          try {
            const data = await fetchMadlibs("");
            const items = Array.isArray(data)
              ? data
              : data.results ?? data.items ?? [];
            setMadlibs(items);
            setServerSearchOK(false);
            setError(null);
          } catch (e2) {
            setError(e2.message || "Failed to load");
          }
        } else {
          setError(e.message || "Failed to load");
        }
      } finally {
        if (mounted.current) setLoading(false);
      }
    })();
    return () => {
      mounted.current = false;
    };
  }, [query]);

  const visibleMadlibs = useMemo(() => {
    if (serverSearchOK || !query) return madlibs;
    const q = query.toLowerCase();
    return madlibs.filter((m) =>
      (m.title || "").toLowerCase().includes(q)
    );
  }, [madlibs, query, serverSearchOK]);

  function onSubmit(e) {
    e.preventDefault();
    setQuery(input.trim());
  }

  return (
    <div className="explore container">
      <div
        className="explore-head"
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: ".75rem",
          margin: "0 0 .5rem",
        }}
      >
        <h1 style={{ margin: 0, fontSize: "1.5rem" }}>Explore</h1>
      </div>

      {/* Search */}
      <form className="searchbar" onSubmit={onSubmit}>
        <input
          className="form-input searchbar-input"
          type="text"
          placeholder="Search madlibs by title…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          aria-label="Search madlibs by title"
        />
        <button className="btn" type="submit">
          Search
        </button>
      </form>

      {/* States */}
      {error && (
        <div className="explore-state explore-state--error">
          <p>Couldn’t load madlibs.</p>
          <code>{error}</code>
          <button
            className="btn"
            onClick={() => {
              setInput("");
              setQuery("");
            }}
          >
            Reset
          </button>
        </div>
      )}

      {loading && <ExploreSkeleton />}

      {!loading && !error && visibleMadlibs.length === 0 && (
        <div className="explore-state">
          <p>No madlibs found.</p>
        </div>
      )}

      {!loading && !error && visibleMadlibs.length > 0 && (
        <div className="explore-grid">
          {visibleMadlibs.map((item) => (
            <MadlibCard key={item.id || item._id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

/*MadlibCard with like count + toggle */
function MadlibCard({ item }) {
  const id = item.id || item._id;
  const title = item.title || "Untitled Madlib";
  const author = item.author?.username || item.username || "Crowdlib Team";

  const [likeCount, setLikeCount] = useState(0);
  const [liked, setLiked] = useState(false);
  const [likeLoading, setLikeLoading] = useState(true);

  // load like count + liked status
  useEffect(() => {
    if (!id) return;

    const loadLikes = async () => {
      try {
        // GET like count: { post_id, likes_count }
        const countRes = await fetch(`${API_ROOT}/likes/${id}/count/`, {
          credentials: "include",
        });
        if (countRes.ok) {
          const json = await countRes.json();
          setLikeCount(json.likes_count ?? 0);
        }

        // GET whether current user liked: { liked: bool }
        const likedRes = await fetch(`${API_ROOT}/likes/${id}/liked/`, {
          credentials: "include",
        });
        if (likedRes.ok) {
          const json = await likedRes.json();
          setLiked(!!json.liked);
        }
      } catch (err) {
        console.error("Error loading like info:", err);
      } finally {
        setLikeLoading(false);
      }
    };

    loadLikes();
  }, [id]);

  // toggle like / unlike
  const handleToggleLike = async () => {
  // must be logged in
// const loggedIn = document.cookie.includes("sessionid=");

// if (!loggedIn) {
//   alert("You must be logged in to like posts.");
//   return;
// }

if (!id || likeLoading) return;
  const csrf = getCookie("csrftoken");
  const url = liked
    ? `${API_ROOT}/likes/${id}/unlike/`
    : `${API_ROOT}/likes/${id}/like/`;

  try {
    const res = await fetch(url, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(csrf ? { "X-CSRFToken": csrf } : {}),
      },
    });

    if (!res.ok) {
      console.warn("Failed to toggle like:", res.status);
      return;
    }

    // Refresh like state from backend
    const countRes = await fetch(`${API_ROOT}/likes/${id}/count/`, {
      credentials: "include",
    });
    if (countRes.ok) {
      const json = await countRes.json();
      setLikeCount(json.likes_count ?? 0);
    }

    // Refresh "liked" state from backend
    const likedRes = await fetch(`${API_ROOT}/likes/${id}/liked/`, {
      credentials: "include",
    });
    if (likedRes.ok) {
      const json = await likedRes.json();
      setLiked(!!json.liked);
    }

  } catch (err) {
    console.error("Error toggling like:", err);
  }
};


  return (
    <article className="card explore-card">
      <div className="explore-body">
        <h3 className="explore-title" style={{ marginTop: ".75rem" }}>
          <Link to={`/madlibs/${id}`}>{title}</Link>
        </h3>

        <p className="explore-meta">
          <span>{author}</span>
        </p>

        <div
          style={{
            display: "flex",
            gap: "1rem",
            marginTop: ".75rem",
            fontSize: "1.1rem",
            alignItems: "center",
          }}
        >
          {/* ❤️ Like button with count */}
          <button
            type="button"
            onClick={handleToggleLike}
            disabled={likeLoading}
            style={{
              background: "none",
              border: "none",
              cursor: likeLoading ? "default" : "pointer",
              fontSize: "1.3rem",
              display: "flex",
              alignItems: "center",
              gap: ".25rem",
              color: liked ? "red" : "#666",
            }}
          >
            <span>{liked ? "❤️" : "🤍"}</span>
            <span style={{ fontSize: ".95rem" }}>{likeCount}</span>
          </button>

          {/* 💬 Comment icon */}
          <Link
            to={`/madlibs/${id}/comments`}
            style={{
              textDecoration: "none",
              cursor: "pointer",
              fontSize: "1.1rem",
            }}
          >
            💬
          </Link>
        </div>
      </div>
    </article>
  );
}

function ExploreSkeleton() {
  return (
    <div className="explore-grid">
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="card explore-card skel">
          <div className="explore-body" style={{ padding: ".9rem" }}>
            <div className="skel-line" />
            <div className="skel-line skel-line--short" />
          </div>
        </div>
      ))}
    </div>
  );
}
