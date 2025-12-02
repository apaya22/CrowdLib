import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const API_ROOT = "http://localhost:8000/api";

function buildTemplatePreview(templateArr) {
  if (!Array.isArray(templateArr)) return "(No preview available)";

  let text = "";
  for (const part of templateArr) {
    if (part.type === "text" && typeof part.content === "string") {
      text += part.content + " ";
    }
    if (text.length > 200) break;
  }

  text = text.trim();

  // Shorten story preview
  const sentenceEnd = text.search(/[.!?]/);
  let preview;
  if (sentenceEnd !== -1 && sentenceEnd < 160) {
    preview = text.slice(0, sentenceEnd + 1);
  } else {
    preview = text.slice(0, 160);
    if (text.length > 160) preview += "…";
  }

  return preview || "(No preview available)";
}

function PostCard({ post }) {
  const { templateTitle, previewText, creatorName, creatorId, createdLabel } =
    post;

  return (
    <article className="card">
      <div className="post-card__body">
        <div className="post-card__meta">
          {templateTitle || "Madlib"}
          {createdLabel && <> · {createdLabel}</>}
        </div>

        <h3 className="post-card__title">
          {templateTitle || "Madlib Story"}
        </h3>

        <p className="post-card__excerpt">{previewText}</p>

        <p
          style={{
            marginTop: "0.5rem",
            fontSize: "0.85rem",
            color: "#6b7280",
          }}
        >
          Posted by{" "}
          <span style={{ fontWeight: 600 }}>
            {creatorName || creatorId || "Unknown user"}
          </span>
        </p>
      </div>

      <footer className="post-card__footer">
        <div className="post-card__stats">
          {/* link to existing comments page */}
          <Link
            className="btn btn--tiny btn--ghost"
            to={`/filled-madlibs/${post._id}/comment`}
          >
            View Post
          </Link>
        </div>
      </footer>
    </article>
  );
}

export default function Posts() {
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      setLoadingPosts(true);
      setError("");

      try {
        // Get ALL filled madlibs
        const res = await fetch(`${API_ROOT}/madlibs/?limit=100`, {
          credentials: "include",
        });

        if (!res.ok) {
          throw new Error(`Failed to load madlibs (HTTP ${res.status})`);
        }

        const data = await res.json();
        const madlibsArray = Array.isArray(data.results)
          ? data.results
          : Array.isArray(data)
          ? data
          : [];

        // For each filled madlib, fill with template and user info
        const hydrated = await Promise.all(
          madlibsArray.map(async (m) => {
            let templateTitle = "";
            let templatePreview = "(No preview available)";
            let createdLabel = "";
            let creatorName = "";
            const creatorId = m.creator_id ? String(m.creator_id) : "";

            // Template fetch
            try {
              if (m.template_id) {
                const tRes = await fetch(
                  `${API_ROOT}/templates/${m.template_id}/`,
                  { credentials: "include" }
                );
                if (tRes.ok) {
                  const tData = await tRes.json();
                  templateTitle = tData.title || "";
                  templatePreview = buildTemplatePreview(tData.template);
                }
              }
            } catch (err) {
              console.error("Failed to load template for madlib:", err);
            }

            // Creator fetch (for username / email)
            try {
              if (creatorId) {
                const uRes = await fetch(
                  `${API_ROOT}/users/${creatorId}/`,
                  { credentials: "include" }
                );
                if (uRes.ok) {
                  const uData = await uRes.json();
                  creatorName =
                    uData.username ||
                    uData.email ||
                    `User ${creatorId.slice(0, 6)}…`;
                }
              }
            } catch (err) {
              console.error("Failed to load creator info:", err);
            }

            // Date label
            const createdRaw =
              m.created_at || m.createdAt || m.timestamp || null;
            if (createdRaw) {
              const d = new Date(createdRaw);
              if (!isNaN(d.getTime())) {
                createdLabel = d.toLocaleDateString();
              }
            }

            return {
              ...m,
              templateTitle,
              previewText: templatePreview,
              creatorName,
              creatorId,
              createdLabel,
            };
          })
        );

        setPosts(hydrated);
      } catch (err) {
        console.error(err);
        setError(err.message || "Failed to load posts.");
      } finally {
        setLoadingPosts(false);
      }
    })();
  }, []);

  if (loadingPosts) {
    return (
      <main className="home">
        <p>Loading posts…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="home">
        <h1 className="section__title">Madlib Feed</h1>
        <p style={{ color: "#b91c1c" }}>{error}</p>
      </main>
    );
  }

  if (!posts.length) {
    return (
      <main className="home">
        <h1 className="section__title">Madlib Feed</h1>
        <p className="section__subtitle">
          No one has posted a filled madlib yet. Be the first!
        </p>
      </main>
    );
  }

  return (
    <main className="home">
      <header className="section">
        <h1 className="section__title">Madlib Feed</h1>
        <p className="section__subtitle">
          All filled madlibs from everyone, for everyone to view and enjoy.
        </p>
      </header>

      <section className="grid grid--3">
        {posts.map((p) => (
          <PostCard key={p._id} post={p} />
        ))}
      </section>
    </main>
  );
}
