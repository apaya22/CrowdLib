import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

/** Demo templates (replace with API later) */
const DEMO_TEMPLATES = [
  {
    id: "funny-day",
    title: "A Funny Day",
    content:
      "Today I saw a very [ADJ] [ANIMAL] at the [NOUN]. It decided to [VERB] while everyone shouted, “What a [ADJ] idea!”",
    tags: ["funny", "animals"],
  },
  {
    id: "space-pirates",
    title: "Space Pirates",
    content:
      "Our spaceship runs on [NOUN] and the captain loves to [VERB] whenever we approach a [ADJ] planet full of [PLURAL NOUN].",
    tags: ["scifi"],
  },
  {
    id: "grandmas-secret",
    title: "Grandma’s Secret",
    content:
      "Grandma’s secret [NOUN] recipe is incredibly [ADJ]. First you [VERB] the [NOUN], then sprinkle with [PLURAL NOUN] and serve.",
    tags: ["family", "food"],
  },
];

/** Extract ordered blanks like [NOUN], [VERB], [ADJ]... */
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

function fillTemplate(text, values) {
  if (!text) return "";
  let i = 0;
  return text.replace(/\[([^\]]+)\]/g, () => {
    const v = values[i];
    i += 1;
    return v && v.trim() ? v : "____";
  });
}

export default function Create() {
  const [mode, setMode] = useState("create");

  // CREATE TEMPLATE state
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  // FILL EXISTING state
  const [searchQuery, setSearchQuery] = useState("");
  const filteredTemplates = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return DEMO_TEMPLATES;
    return DEMO_TEMPLATES.filter(
      (t) =>
        t.title.toLowerCase().includes(q) ||
        (t.tags || []).some((tag) => tag.toLowerCase().includes(q))
    );
  }, [searchQuery]);

  const [selectedId, setSelectedId] = useState(DEMO_TEMPLATES[0].id);
  const selectedTemplate = useMemo(
    () => DEMO_TEMPLATES.find((t) => t.id === selectedId),
    [selectedId]
  );
  const blanks = useMemo(
    () => extractBlanks(selectedTemplate?.content || ""),
    [selectedTemplate]
  );
  const [fillValues, setFillValues] = useState([]);
  const safeFillValues = useMemo(() => {
    const arr = [...fillValues];
    arr.length = blanks.length;
    return arr.map((v) => v || "");
  }, [blanks.length, fillValues]);

  function handleFillChange(i, val) {
    setFillValues((prev) => {
      const copy = [...prev];
      copy[i] = val;
      return copy;
    });
  }

  function onSubmitCreate(e) {
    e.preventDefault(); // template only
  }
  function onSubmitFill(e) {
    e.preventDefault(); // template only
  }

  const filledPreview = useMemo(
    () => fillTemplate(selectedTemplate?.content || "", safeFillValues),
    [selectedTemplate, safeFillValues]
  );

  return (
    <div className="create container">
      <div className="create-head">
        <h1>Create & Play</h1>
        <div className="tabs">
          <button
            type="button"
            className={`tab ${mode === "create" ? "tab--active" : ""}`}
            onClick={() => setMode("create")}
          >
            Create a Template
          </button>
          <button
            type="button"
            className={`tab ${mode === "fill" ? "tab--active" : ""}`}
            onClick={() => setMode("fill")}
          >
            Play a Madlib
          </button>
        </div>
      </div>

      {/* CREATE A TEMPLATE */}
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
            />
            <small className="form-hint">
              Use brackets <code>[ ]</code> to mark blanks (e.g., <code>[NOUN]</code>).
            </small>
          </div>

          <div className="create-actions">
            <div className="action-buttons">
              <button className="btn btn--primary" type="submit" disabled title="Placeholder">
                Publish Template
              </button>
            </div>
          </div>
        </form>
      )}

      {/* FILL EXISTING TEMPLATE */}
      {mode === "fill" && (
        <form className="card create-form" onSubmit={onSubmitFill} noValidate>
          <div className="form-row">
            <label className="form-label" htmlFor="templateSearch">Search for a Story</label>
            <input
              id="templateSearch"
              className="form-input"
              type="text"
              placeholder="Search stories by title or tag…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />

            <div className="template-results">
              {filteredTemplates.length > 0 ? (
                filteredTemplates.map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    className={`template-result ${selectedId === t.id ? "template-result--active" : ""}`}
                    onClick={() => { setSelectedId(t.id); setFillValues([]); }}
                  >
                    <div className="template-title">{t.title}</div>
                    {t.tags?.length > 0 && (
                      <div className="template-tags">
                        {t.tags.map((tag) => (
                          <span key={tag} className="tag">#{tag}</span>
                        ))}
                      </div>
                    )}
                  </button>
                ))
              ) : (
                <p className="muted" style={{ marginTop: ".5rem" }}>No templates found.</p>
              )}
            </div>
          </div>

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
              <p>No blanks detected in this template.</p>
            </div>
          )}

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
              <Link className="btn" to="/login" title="Requires auth (placeholder)">Generate AI</Link>
              <button className="btn btn--primary" type="submit" disabled title="Placeholder">
                Publish Filled Story
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
