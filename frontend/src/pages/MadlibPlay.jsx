import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const API_ROOT = (import.meta.env.VITE_API_BASE || "http://localhost:8000/api").replace(/\/$/, "");

function renderStory(templateArr, values) {
  if (!Array.isArray(templateArr)) return "";

  let out = "";

  templateArr.forEach((part) => {
    if (part.type === "text") {
      out += part.content || "";
    } else if (part.type === "blank") {
      const id = String(part.id);
      out += values[id] || "";
    }
  });

  return out;
}


export default function MadlibPlay() {
  const { id } = useParams(); // template id from /madlibs/:id

  const [template, setTemplate] = useState(null);
  const [values, setValues] = useState({});
  const [me, setMe] = useState(null);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // load current user (for saving)
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_ROOT}/users/me/`, { credentials: "include" });
        if (r.ok) setMe(await r.json());
      } catch {
        // ignore
      }
    })();
  }, []);

  // load template by id
  useEffect(() => {
    (async () => {
      setLoading(true);
      setError("");
      try {
        const r = await fetch(`${API_ROOT}/templates/${id}/`, { credentials: "include" });
        if (!r.ok) throw new Error(`Failed to load template (HTTP ${r.status})`);
        const data = await r.json(); // expects { _id, title, template, blanks:[{id,...}] }
        setTemplate(data);

        const init = {};
        (data.blanks || []).forEach((b) => {
          init[String(b.id)] = "";
        });
        setValues(init);
      } catch (e) {
        setError(e.message || "Failed to load template");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  // render and persist a filled madlib
  async function onSubmit(e) {
    e.preventDefault();
    setError("");

    // pick the story text from the template
    const filled = renderStory(template.template, values);

    setResult(filled);

    // optional save
    try {
      if (!me?.id) return;

      const inputted_blanks = Object.entries(values).map(([k, v]) => ({
        id: String(k),
        input: String(v),
      }));

      const res = await fetch(`${API_ROOT}/madlibs/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          template_id: String(id),
          creator_id: String(me.id),
          inputted_blanks,
        }),
      });

      if (!res.ok) {
        const t = await res.text().catch(() => "");
        console.warn("Save failed:", res.status, t);
      }
    } catch (e) {
      console.warn("Save error:", e);
    }
  }

  // states
  if (loading) return <main style={{ padding: "2rem" }}>Loading…</main>;
  if (error) return <main style={{ padding: "2rem", color: "red" }}>{error}</main>;
  if (!template) return <main style={{ padding: "2rem" }}>Not found.</main>;

  return (
    <main style={{ maxWidth: 900, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>{template.title || "Untitled"}</h1>

      {(template.blanks?.length ?? 0) === 0 ? (
        <p style={{ whiteSpace: "pre-wrap", marginTop: "1rem" }}>
          {template.template || template.story || "No story provided."}
        </p>
      ) : (
        <form onSubmit={onSubmit} style={{ display: "grid", gap: "0.75rem", marginTop: "1rem" }}>
          {(template.blanks || []).map((b) => {
            const label =
              b.label ||
              b.prompt ||
              b.hint ||
              b.wordType ||
              b.type ||
              (b.placeholder && b.placeholder.toLowerCase() !== "blank" ? b.placeholder : null) ||
              `Blank #${b.id}`;

            const ph =
              b.placeholder && b.placeholder.toLowerCase() !== "blank"
                ? b.placeholder
                : label;

            return (
              <label key={b.id} style={{ display: "grid", gap: "0.25rem" }}>
                <span style={{ opacity: 0.7 }}>{label}</span>
                <input
                  value={values[String(b.id)] ?? ""}
                  onChange={(e) => setValues((v) => ({ ...v, [String(b.id)]: e.target.value }))}
                  placeholder={ph}
                  autoComplete="off"
                  required
                />
              </label>
            );
          })}

          <button type="submit">Generate</button>
        </form>
      )}

      {result && (
        <section
          style={{
            marginTop: "1.5rem",
            padding: "1rem",
            border: "1px solid #eee",
            borderRadius: 12,
          }}
        >
          <h3>Result</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{result}</p>
        </section>
      )}
    </main>
  );
}
