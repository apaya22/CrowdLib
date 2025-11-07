import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";

const API_ROOT = (import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api").replace(/\/$/, "");

export default function Explore() {
  // set states
  const mounted = useRef(true);

  const [madlibs, setMadlibs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");
  const [serverSearchOK, setServerSearchOK] = useState(true);
  // get from API
  async function fetchMadlibs(q = "") {
    const url = new URL(`${API_ROOT}/templates/`);
    if (q) url.searchParams.set("search", q);
    const res = await fetch(url.toString(), {
      credentials: "include",
    });
    if (!res.ok) {
      const txt = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} :: ${txt.slice(0, 160)}`);
    }
    return res.json();
  }

  // load and search
  useEffect(() => {
    mounted.current = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchMadlibs(query);
        if (!mounted.current) return;

        const items = Array.isArray(data) ? data : (data.results ?? data.items ?? []);
        setMadlibs(items);
        setServerSearchOK(true);
      } catch (e) {
        if (query) {
          try {
            const data = await fetchMadlibs("");
            const items = Array.isArray(data) ? data : (data.results ?? data.items ?? []);
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
    return () => { mounted.current = false; };
  }, [query]);

  // show madlibs
  const visibleMadlibs = useMemo(() => {
    if (serverSearchOK || !query) return madlibs;
    const q = query.toLowerCase();
    return madlibs.filter(m =>
      (m.title || "").toLowerCase().includes(q)
    );
  }, [madlibs, query, serverSearchOK]);

  // submit function
  function onSubmit(e) {
    e.preventDefault();
    setQuery(input.trim());
  }
  // html styling
  return (
    <div className="explore container">
      {/* Header */}
      <div className="explore-head" style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:".75rem",margin:"0 0 .5rem"}}>
        <h1 style={{margin:0,fontSize:"1.5rem"}}>Explore</h1>
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
        <button className="btn" type="submit">Search</button>
      </form>

      {/* States */}
      {error && (
        <div className="explore-state explore-state--error">
          <p>Couldn’t load madlibs.</p>
          <code>{error}</code>
          <button className="btn" onClick={() => { setInput(""); setQuery(""); }}>Reset</button>
        </div>
      )}

      {loading && <ExploreSkeleton />}

      {!loading && !error && visibleMadlibs.length === 0 && (
        <div className="explore-state">
          <p>No madlibs found.</p>
        </div>
      )}

      {/* Grid of madlibs only */}
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
// display madlib and information
function MadlibCard({ item }) {
  const id = item.id || item._id;
  const title = item.title || "Untitled Madlib";
  const author = item.author?.username || item.username || "Crowdlib Team";

  return (
    <article className="card explore-card">
      <div className="explore-body">
        <h3 className="explore-title" style={{marginTop: ".75rem"}}>
          <Link to={`/madlibs/${id}`}>{title}</Link>
        </h3>
        <p className="explore-meta">
          <span>{author}</span>
        </p>
      </div>
    </article>
  );
}

function ExploreSkeleton() {
  return (
    <div className="explore-grid">
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="card explore-card skel">
          <div className="explore-body" style={{padding: ".9rem"}}>
            <div className="skel-line" />
            <div className="skel-line skel-line--short" />
          </div>
        </div>
      ))}
    </div>
  );
}
