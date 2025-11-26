import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const API_ROOT = "http://localhost:8000/api";

function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='));

    return cookieValue ? cookieValue.split('=')[1] : null;
}

// Parser for user story template
function parseStory(raw) {
  const story = raw || "";
  const template = [];
  const blanksMap = {};
  let blankIdCounter = 0; // Track by ID

  const regex = /\[([^\]]+)\]/g; // find all pairs []
  let cursor = 0;
  let match;

  // Extract all blanks
  while ((match = regex.exec(story)) !== null) {
    const before = story.slice(cursor, match.index);
    if (before) {
      template.push({
        type: "text",
        content: before,
      });
    }

    // Normalize wording for API
    const rawWordType = match[1].trim();
    if (rawWordType) {
      blankIdCounter += 1;
      const id = String(blankIdCounter);
      const normalized = rawWordType
        .toLowerCase()
        .replace(/\s+/g, "_");

      const blankObj = {
        type: "blank",
        wordType: normalized,
        id,
      };

      template.push(blankObj);
      blanksMap[id] = blankObj;
    }

    cursor = match.index + match[0].length;
  }

  // get final text after word (fixed text after last blank issue)
  const after = story.slice(cursor);
  if (after) {
    template.push({
      type: "text",
      content: after,
    });
  }

  // create blank array for Django
  const blanks = Object.keys(blanksMap)
    .sort((a, b) => Number(a) - Number(b))
    .map((id) => blanksMap[id]);

  return { template, blanks, blankCount: blanks.length };
}

// create() component state
export default function Create() {
  const [title, setTitle] = useState("");
  const [story, setStory] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [createdId, setCreatedId] = useState(null);

  const navigate = useNavigate();
  const location = useLocation();

  // submits to backend, checks for errors
  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setCreatedId(null);

    if (!title.trim()) {
      setError("Please provide a title.");
      return;
    }
    if (!story.trim()) {
      setError("Please write a story.");
      return;
    }

    const { template, blanks, blankCount } = parseStory(story);
    
    // make sure valid structure
    if (template.length === 0) {
      setError("Your template is empty. Add some text and blanks first.");
      return;
    }
    if (blankCount === 0) {
      setError(
        "You must include at least one blank. Use [NOUN], [VERB], [ADJECTIVE], etc. in your story."
      );
      return;
    }

    const payload = {
      title: title.trim(),
      story: story.trim(),
      blank_count: blankCount,
      template,
      blanks,
    };

    const csrftoken = getCookie("csrftoken");

    try {
      setSaving(true);
      
      // Make POST request
      const res = await fetch(`${API_ROOT}/templates/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(csrftoken ? { "X-CSRFToken": csrftoken } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (res.status === 401 || res.status === 403) {
        setError("You must be logged in to publish a template.");
        navigate("/login", { replace: false, state: { from: location } });
        return;
      }

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        console.error("Template create failed:", res.status, text);
        throw new Error(`HTTP ${res.status}: ${text.slice(0, 300)}`);
      }

      const data = await res.json().catch(() => ({}));
      const id = data._id || data.id || null;

      setCreatedId(id);
      setTitle("");
      setStory("");
    } catch (err) {
      setError(err.message || "Failed to publish template.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="container create">
      <header className="create-header">
        <h1>Create a Madlib Template</h1>
        <p className="muted">
          Create your own template Madlib for others to play and enjoy!
        </p>
      </header>

      <section className="card create-card">
        <form className="create-form" onSubmit={handleSubmit} noValidate>
          <div className="form-row">
            <label className="form-label" htmlFor="title">
              Title <span className="required">*</span>
            </label>
            <input
              id="title"
              className="form-input"
              type="text"
              placeholder="e.g., The Superhero Job Interview"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="form-row">
            <label className="form-label" htmlFor="story">
              Story{" "}
              <span className="form-hint-inline">
                (use blanks like <code>[noun]</code>, <code>[verb]</code>,{" "}
                <code>[adjective]</code>, etc.)
              </span>
            </label>
            <textarea
              id="story"
              className="form-textarea"
              rows={10}
              placeholder={`Example:
Today I had an interview to become a professional [noun]. The interviewer asked me to [verb] a [adjective] building in under [number] seconds...`}
              value={story}
              onChange={(e) => setStory(e.target.value)}
            />
            <p className="form-hint">
              Blanks for your story must be in brackets <code>[blank]</code> in order to display properly to other users. You can edit templates under your profile.
            </p>
          </div>

          {error && (
            <p className="form-message form-message--error">{error}</p>
          )}

          {createdId && (
            <p className="form-message form-message--success">
              Template published! Generated ID:&nbsp;
              <code>{createdId}</code>
            </p>
          )}

          <div className="create-actions">
            <button
              type="submit"
              className="btn btn--primary"
              disabled={saving}
            >
              {saving ? "Publishing…" : "Publish Template"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
