import { useEffect, useState } from "react";
import { Link } from "react-router-dom";


const API = "http://127.0.0.1:8000/api/madlibs/";

export default function Explore() {
  const [madlibs, setMadlibs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(API);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        //{ madlibs: [...], count: N }
        const data = await res.json();
        setMadlibs(data.madlibs || []);
      } catch (e) {
        setError(e.message || "Failed to load madlibs");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <p>Loading…</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;

  return (
    <div style={{ maxWidth: 900, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Explore Madlibs</h1>
      {!madlibs.length ? (
        <p>No madlibs yet.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {madlibs.map((m) => (
            <li
              key={m._id}
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                padding: "1rem",
                margin: ".75rem 0",
                transition: "background 0.2s",
              }}
            >
              <h3 style={{ margin: 0 }}>
                <Link
                  to={`/madlibs/${m._id}`}
                  style={{
                    textDecoration: "none",
                    color: "black",
                    fontWeight: 700,
                  }}
                >
                  {m.title}
                </Link>
              </h3>
              <div style={{ opacity: 0.7 }}>Blanks: {m.blank_count}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
