import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

/* placefholder for when oauth workds */
//import { useAuth } from "../pages/Signup.jsx";

const useAuth = () => ({ user: null });

// search for placeholders: [NOUN] in text 
function extractBlanks(text) {
  if (!text) return [];
  const regex = /\[([^\]]+)\]/g;
  const blanks = [];
  let match;
  const counts = {};
  while ((match = regex.exec(text)) !== null) {
    const label = match[1].trim();
    counts[label] = (counts[label] || 0) + 1;
    blanks.push({ label, index: counts[label], token: `[${label}]` });
  }
  return blanks;
}

// fill with user's choices
function fillTemplate(text, values) {
  if (!text) return "";
  let i = 0;
  return text.replace(/\[([^\]]+)\]/g, () => {
    const v = values[i];
    i += 1;
    return v && v.trim() ? v : "____";
  });
}

// for when they need to post (Needs work)
function getCookie(name) {
  const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return m ? m.pop() : "";
}

/* Play & Create */
export default function Create() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState("fill");

  // API base
  const API_ROOT =
    (import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api").replace(/\/$/, "");
  
  // search box
  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");
  const [templates, setTemplates] = useState([]);

  // handle errors
  const [tplLoading, setTplLoading] = useState(true);
  const [tplError, setTplError] = useState(null);

  // store typed words
  const [selectedId, setSelectedId] = useState(null);
  const selectedTemplate = useMemo(
    () => templates.find(t => (t.id ?? t._id) === selectedId),
    [selectedId, templates]
  );
  const blanks = useMemo(
    () => extractBlanks(selectedTemplate?.content || ""),
    [selectedTemplate]
  );
  const [fillValues, setFillValues] = useState([]);
  const safeFillValues = useMemo(() => {
    const arr = [...fillValues];
    arr.length = blanks.length;
    return arr.map(v => v || "");
  }, [blanks.length, fillValues]);

  function handleFillChange(i, val) {
    setFillValues(prev => {
      const copy = [...prev];
      copy[i] = val;
      return copy;
    });
  }

  // show preview text
  const filledPreview = useMemo(
    () => fillTemplate(selectedTemplate?.content || "", safeFillValues),
    [selectedTemplate, safeFillValues]
  );

  // get templates from server
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setTplLoading(true);
        setTplError(null);
        const url = new URL(`${API_ROOT}/templates/`);
        if (query) url.searchParams.set("search", query); // does drf seach filter work?
        const res = await fetch(url.toString(), {
          credentials: "include",
        });
        if (!res.ok) {
          const t = await res.text().catch(() => "");
          throw new Error(`HTTP ${res.status} :: ${t.slice(0,160)}`);
        }
        const data = await res.json();
        if (!mounted) return;
        const items = Array.isArray(data) ? data : (data.results ?? data.items ?? []);
        setTemplates(items);
        // choose first as selected
        if (!selectedId && items.length > 0) {
          setSelectedId(items[0].id ?? items[0]._id);
          setFillValues([]); // reset fills
        }
      } catch (e) {
        if (!mounted) return;
        setTplError(e.message || "Failed to load templates");
      } finally {
        if (mounted) setTplLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [query, API_ROOT]);

  // Create template
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  async function requireAuthOrRedirect() { // must be logged in
    if (user) return true;
    navigate("/login", { replace: true, state: { from: location } });
    return false;
  }

  async function onSubmitCreate(e) {
    e.preventDefault();
    if (!(await requireAuthOrRedirect())) return;

    try {
      const csrftoken = getCookie("csrftoken");
      const res = await fetch(`${API_ROOT}/templates/`, {
        method: "POST",
        credentials: "include", // send session cookie
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken || "",
        },
        body: JSON.stringify({ title, content, tags: [] }),
      });
      if (!res.ok) {
        const t = await res.text().catch(() => "");
        throw new Error(`HTTP ${res.status} :: ${t.slice(0,200)}`);
      }
      // success -> refresh list and switch to "fill" so they can play it
      setTitle("");
      setContent("");
      setMode("fill");
      // trigger a re-search to include the new template
      setInput(title);
      setQuery(title);
    } catch (err) {
      alert(err.message || "Failed to create template");
    }
  }

  function onSubmitFill(e) { // Needs work for posting and AI image generation
    e.preventDefault();
  }

  function onSearchSubmit(e) {
    e.preventDefault();
    setQuery(input.trim());
  }

  // html layout
  return (
    <div className="create container">
      <div className="create-head">
        <h1>Create & Play</h1>
        <div className="tabs">
          <button
            type="button"
            className={`tab ${mode === "fill" ? "tab--active" : ""}`}
            onClick={() => setMode("fill")}
          >
            Play a Madlib
          </button>
          <button
            type="button"
            className={`tab ${mode === "create" ? "tab--active" : ""}`}
            onClick={() => setMode("create")}
          >
            Create a Template
          </button>
        </div>
      </div>

      {/* PLAY */}
      {mode === "fill" && (
        <form className="card create-form" onSubmit={onSubmitFill} noValidate>
          {/* Search templates */}
          <div className="form-row">
            <label className="form-label" htmlFor="templateSearch">Search for a Story</label>
            <form onSubmit={onSearchSubmit} style={{ display: "flex", gap: ".5rem" }}>
              <input
                id="templateSearch"
                className="form-input"
                type="text"
                placeholder="Search stories by title…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
              <button className="btn" type="submit">Search</button>
            </form>

            {/* Results list */}
            <div className="template-results" style={{ marginTop: ".5rem" }}>
              {tplLoading && <p className="muted">Loading…</p>}
              {tplError && (
                <div className="explore-state explore-state--error">
                  <p>Couldn’t load templates.</p>
                  <code>{tplError}</code>
                </div>
              )}
              {!tplLoading && !tplError && templates.length === 0 && (
                <p className="muted">No templates found.</p>
              )}
              {!tplLoading && !tplError && templates.length > 0 && (
                templates.map((t) => {
                  const tid = t.id ?? t._id;
                  return (
                    <button
                      key={tid}
                      type="button"
                      className={`template-result ${selectedId === tid ? "template-result--active" : ""}`}
                      onClick={() => { setSelectedId(tid); setFillValues([]); }}
                    >
                      <div className="template-title">{t.title || "Untitled"}</div>
                      {Array.isArray(t.tags) && t.tags.length > 0 && (
                        <div className="template-tags">
                          {t.tags.map((tag) => (
                            <span key={tag} className="tag">#{tag}</span>
                          ))}
                        </div>
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Dynamic blanks */}
          {blanks.length > 0 ? (
            <div className="blanks-grid">
              {blanks.map((b, i) => (
                <div key={`${b.label}-${i}`} className="form-row">
                  <label className="form-label">
                    {b.label} <span className="muted">#{b.index}</span>
                  </label>
                  <input
                    className="form-input"
                    type="text"
                    placeholder={b.token}
                    value={safeFillValues[i]}
                    onChange={(e) => handleFillChange(i, e.target.value)}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="explore-state">
              <p>Select a template to play.</p>
            </div>
          )}
          
          {/* Preview only (AI not implemented yet) check if POST works in backend */}
          <div className="create-actions">
            <div className="create-preview card">
              <div className="img-placeholder img-placeholder--wide" aria-hidden>
                <span>AI Image Preview (placeholder)</span>
              </div>
              <div className="preview-body">
                <h3 className="preview-title">
                  {selectedTemplate?.title || "Selected Template"}
                </h3>
                <p className="preview-text">
                  {filledPreview || "Your filled story preview will appear here."}
                </p>
              </div>
            </div>
            <div className="action-buttons">
              {}
              <Link className="btn" to="/login" title="Requires auth (placeholder)">Generate AI</Link>
              <Link className="btn btn--primary" to="/login" title="Requires auth (placeholder)">
                Post
              </Link>
            </div>
          </div>
        </form>
      )}

      {/* CREATE A NEW TEMPLATE (requires login) */}
      {mode === "create" && (
        <form className="card create-form" onSubmit={onSubmitCreate} noValidate>
          <div className="form-row">
            <label className="form-label" htmlFor="title">Title</label>
            <input
              id="title"
              className="form-input"
              type="text"
              placeholder="e.g., The [ADJ] Adventure"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-row">
            <label className="form-label" htmlFor="content">
              Story (use blanks like [NOUN], [VERB], [ADJ], [PLURAL NOUN]…)
            </label>
            <textarea
              id="content"
              className="form-textarea"
              rows={10}
              placeholder={`Today I saw a [ADJ] [ANIMAL] who loved to [VERB] at the [NOUN]...`}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
            />
            <small className="form-hint">
              Use brackets <code>[ ]</code> to mark blanks (e.g., <code>[NOUN]</code>).
            </small>
          </div>

          <div className="create-actions">
            <div className="action-buttons">
              <button className="btn btn--primary" type="submit">
                Publish Template
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
