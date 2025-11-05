import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

const API_BASE =
  import.meta.env.VITE_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8000/api/madlibs/";

export default function Explore() {
  const mounted = useRef(true);
  const [madlibs, setMadlibs] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    mounted.current = true;
    const ctrl = new AbortController();

    async function run() {
      try {
        if (page === 1) {
          setLoading(true);
          setError(null);
        } else {
          setLoadingMore(true);
        }

        const res = await fetch(`${API_BASE}/madlibs/?page=${page}&limit=12`, {
          signal: ctrl.signal,
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (!mounted.current) return;

        const list = Array.isArray(data?.madlibs) ? data.madlibs : [];
        setMadlibs((prev) => (page === 1 ? list : [...prev, ...list]));
        setTotal(Number(data?.count ?? list.length));
      } catch (e) {
        if (e.name !== "AbortError") setError(e.message || "Failed to load");
      } finally {
        if (!mounted.current) return;
        setLoading(false);
        setLoadingMore(false);
      }
    }

    run();
    return () => {
      mounted.current = false;
      ctrl.abort();
    };
  }, [page]);

  const hasMore = madlibs.length < total;

  return (
    <div className="explore container">
      <div className="explore-head" style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:".75rem",margin:"0 0 .5rem"}}>
        <h1 style={{margin:0,fontSize:"1.5rem"}}>Explore</h1>
        <Link className="btn btn--secondary" to="/create">Create</Link>
      </div>

      {error && (
        <div className="explore-state explore-state--error">
          <p>Couldn’t load explore feed.</p>
          <code>{error}</code>
          <button className="btn" onClick={() => { setPage(1); }}>Retry</button>
        </div>
      )}

      {loading && <ExploreSkeleton />}

      {!loading && !error && madlibs.length === 0 && (
        <div className="explore-state">
          <p>No posts yet. Be the first to create one!</p>
          <Link className="btn btn--primary" to="/create">Create a Madlib</Link>
        </div>
      )}

      {!loading && !error && madlibs.length > 0 && (
        <>
          <div className="explore-grid">
            {madlibs.map((item) => (
              <ExploreCard key={item._id || item.id} item={item} />
            ))}
          </div>

          {hasMore && (
            <div className="explore-more">
              <button
                className="btn"
                onClick={() => setPage((p) => p + 1)}
                disabled={loadingMore}
              >
                {loadingMore ? "Loading…" : "Load more"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ExploreCard({ item }) {
  const id = item._id || item.id;
  const title = item.title || "Untitled Madlib";
  const username = item.username || item.author || "@user";
  const likes = item.likes ?? 0;
  const comments = item.comments ?? 0;

  return (
    <article className="card explore-card">
      <Link className="explore-thumb img-placeholder" to={`/post/${id}`} aria-label={`Open ${title}`}>
        <span>Image</span>
      </Link>

      <div className="explore-body">
        <h3 className="explore-title">
          <Link to={`/post/${id}`}>{title}</Link>
        </h3>

        <p className="explore-meta">
          <span>{username}</span>
          <span>•</span>
          <span>❤️ {likes}</span>
          <span>💬 {comments}</span>
        </p>

        <div style={{display:"flex",gap:".5rem"}}>
          <Link className="btn btn--tiny" to={`/post/${id}`}>View</Link>
          <Link className="btn btn--tiny" to="/login">Like</Link>
          <Link className="btn btn--tiny" to="/login">Comment</Link>
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
          <div className="explore-thumb skel-box" />
          <div className="explore-body">
            <div className="skel-line" />
            <div className="skel-line skel-line--short" />
          </div>
        </div>
      ))}
    </div>
  );
}