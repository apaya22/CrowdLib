import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

const API_ROOT = (import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api").replace(/\/$/, "");

export default function Comment() {
  const { id } = useParams();

  const [madlib, setMadlib] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [comment, setComment] = useState("");

  useEffect(() => {
    async function loadMadlib() {
      try {
        setLoading(true);
        const res = await fetch(`${API_ROOT}/templates/${id}/`, {
          credentials: "include",
        });

        if (!res.ok) {
          throw new Error("Failed to load madlib");
        }

        const data = await res.json();
        setMadlib(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadMadlib();
  }, [id]);

  if (loading) return <p style={{ padding: "1rem" }}>Loading…</p>;
  if (error) return <p style={{ color: "red", padding: "1rem" }}>{error}</p>;

  return (
    <div style={{ maxWidth: "600px", margin: "2rem auto" }}>
      <h1 style={{ color: "#5a0fb3" }}>
        {madlib?.title || "Untitled Madlib"}
      </h1>

      <h3 style={{ marginTop: "1.5rem" }}>Leave a comment</h3>

      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Write your comment..."
        style={{
          width: "100%",
          height: "150px",
          padding: "1rem",
          fontSize: "1rem",
          borderRadius: "8px",
          border: "1px solid #ccc",
          resize: "vertical",
        }}
      />

      <button
        style={{
          marginTop: "1rem",
          padding: ".75rem 1.25rem",
          background: "#5a0fb3",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
          fontSize: "1rem",
        }}
      >
        Submit Comment
      </button>
    </div>
  );
}
