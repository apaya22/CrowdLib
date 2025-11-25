import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const BACKEND = "http://localhost:8000";

// Get CSRF cookie
function getCookie(name) {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith(name + "="));
  return cookieValue ? cookieValue.split("=")[1] : null;
}

export default function Profile() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [madlibs, setMadlibs] = useState([]);
  const [madlibsLoading, setMadlibsLoading] = useState(true);
  const [templates, setTemplates] = useState({});
  const [expandedMadlibs, setExpandedMadlibs] = useState({});
  const [likeCounts, setLikeCounts] = useState({}); // NEW: Store like counts

  /* fetch profile */
  useEffect(() => {
    async function loadProfile() {
      try {
        const res = await fetch(`${BACKEND}/api/users/profile/`, {
          method: "GET",
          credentials: "include",
        });

        if (!res.ok) {
          console.error("Profile load failed:", await res.text());
          setLoading(false);
          return;
        }

        const user = await res.json();
        setData(user);
      } catch (err) {
        console.error("Error fetching profile:", err);
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  /* fetch user's madlibs */
  useEffect(() => {
    async function loadMadlibs() {
      if (!data?._id) return;

      try {
        setMadlibsLoading(true);
        const res = await fetch(`${BACKEND}/api/madlibs/by_creator/?creator_id=${data._id}`, {
          method: "GET",
          credentials: "include",
        });

        if (!res.ok) {
          console.error("Failed to load madlibs:", await res.text());
          setMadlibsLoading(false);
          return;
        }

        const userMadlibs = await res.json();
        setMadlibs(userMadlibs);

        // Fetch templates for each madlib
        const templateIds = [...new Set(userMadlibs.map(m => m.template_id))];
        const templateData = {};
        
        for (const templateId of templateIds) {
          try {
            const templateRes = await fetch(`${BACKEND}/api/templates/${templateId}/`, {
              credentials: "include",
            });
            if (templateRes.ok) {
              const template = await templateRes.json();
              templateData[templateId] = template;
            }
          } catch (err) {
            console.error(`Failed to load template ${templateId}:`, err);
          }
        }
        
        setTemplates(templateData);

        // NEW: Fetch like counts for each madlib
        const likeData = {};
        for (const madlib of userMadlibs) {
          try {
            const likeRes = await fetch(`${BACKEND}/api/likes/${madlib._id}/count/`, {
              credentials: "include",
            });
            if (likeRes.ok) {
              const likeJson = await likeRes.json();
              likeData[madlib._id] = likeJson.likes_count || 0;
            }
          } catch (err) {
            console.error(`Failed to load likes for madlib ${madlib._id}:`, err);
            likeData[madlib._id] = 0;
          }
        }
        
        setLikeCounts(likeData);
      } catch (err) {
        console.error("Error fetching madlibs:", err);
      } finally {
        setMadlibsLoading(false);
      }
    }

    loadMadlibs();
  }, [data]);

  /* delete account */
  async function handleDeleteAccount() {
    const csrf = getCookie("csrftoken");

    if (!csrf) {
      alert("Missing CSRF token.");
      return;
    }

    try {
      const id = data._id;
      const res = await fetch(`${BACKEND}/api/users/${id}/`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrf,
        },
      });

      if (!res.ok) {
        alert("Account delete failed.");
        return;
      }

      alert("Account deleted.");
      window.location.href = "/";
    } catch (err) {
      console.error("Delete account error:", err);
    }
  }

  /* delete madlib */
  async function handleDeleteMadlib(madlibId) {
    const csrf = getCookie("csrftoken");

    if (!csrf) {
      alert("Missing CSRF token.");
      return;
    }

    if (!confirm("Are you sure you want to delete this madlib?")) {
      return;
    }

    try {
      const res = await fetch(`${BACKEND}/api/madlibs/${madlibId}/`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrf,
        },
      });

      if (!res.ok) {
        alert("Failed to delete madlib.");
        return;
      }

      // Remove from local state
      setMadlibs(madlibs.filter(m => m._id !== madlibId));
      alert("Madlib deleted successfully!");
    } catch (err) {
      console.error("Delete madlib error:", err);
      alert("Error deleting madlib.");
    }
  }

  // Edit Mode
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({
    username: "",
    bio: "",
    profile_picture: "",
  });

  useEffect(() => {
    if (data) {
      setForm({
        username: data.username || "",
        bio: data.bio || "",
        profile_picture: data.profile_picture || "",
      });
    }
  }, [data]);

  /* Handler Update */
  async function handleUpdate() {
    const csrf = getCookie("csrftoken");
    if (!csrf) {
      alert("Missing CSRF token.");
      return;
    }

    try {
      const res = await fetch(`${BACKEND}/api/users/${data._id}/`, {
        method: "PUT",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrf,
        },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        console.error("Update failed:", await res.text());
        alert("Update failed.");
        return;
      }

      // Refresh After Edit
      const refreshed = await fetch(`${BACKEND}/api/users/profile/`, {
        method: "GET",
        credentials: "include",
      }).then((r) => r.json());

      setData(refreshed);
      setEditMode(false);
      alert("Profile updated!");
    } catch (err) {
      console.error("Error updating profile:", err);
      alert("Error updating profile.");
    }
  }

  /* Render story with filled blanks */
  function renderFilledStory(template, filledBlanks) {
    if (!template?.template || !Array.isArray(template.template)) {
      return "Story not available";
    }

    // Create a map of blank ID to filled input
    const blanksMap = {};
    filledBlanks.forEach(blank => {
      blanksMap[String(blank.id)] = blank.input;
    });

    let result = "";
    template.template.forEach(part => {
      if (part.type === "text") {
        result += part.content || "";
      } else if (part.type === "blank") {
        const filledValue = blanksMap[String(part.id)] || `[${part.id}]`;
        result += filledValue;
      }
    });

    return result;
  }

  /* Toggle expand/collapse */
  function toggleExpand(madlibId) {
    setExpandedMadlibs(prev => ({
      ...prev,
      [madlibId]: !prev[madlibId]
    }));
  }

  /* Render */
  if (loading) {
    return <div style={{ padding: "20px" }}>Loading profile…</div>;
  }

  if (!data) {
    return <div style={{ padding: "20px" }}>Could not load profile.</div>;
  }

  const profilePic = data.profile_picture || null;

  return (
    <div style={{ padding: "20px" }}>
      <h1>Your Profile</h1>

      <div
        style={{
          maxWidth: "480px",
          border: "1px solid #ddd",
          borderRadius: "10px",
          padding: "20px",
          marginTop: "15px",
          boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        }}
      >
        {!editMode ? (
          <>
            <div style={{ marginBottom: "10px" }}>
              <strong>Username:</strong> {data.username}
            </div>
            <div style={{ marginBottom: "10px" }}>
              <strong>Email:</strong> {data.email}
            </div>
            <div style={{ marginBottom: "10px" }}>
              <strong>Bio:</strong> {data.bio || "No bio yet."}
            </div>
            <div style={{ marginBottom: "10px" }}>
              <strong>Picture:</strong>
              <br />
              {data.profile_picture ? (
                <img
                  src={profilePic}
                  alt="pfp"
                  style={{ width: "120px", height: "120px", objectFit: "cover", borderRadius: "12px" }}
                />
              ) : (
                "No picture"
              )}
            </div>

            <button
              style={{
                padding: "8px 14px",
                background: "#444",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                marginRight: "10px",
              }}
              onClick={() => setEditMode(true)}
            >
              Edit Profile
            </button>

            <button
              onClick={handleDeleteAccount}
              style={{
                padding: "8px 14px",
                backgroundColor: "#d11a2a",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontWeight: 600,
              }}
            >
              Delete Account
            </button>
          </>
        ) : (
          <>
            <label>Username:</label>
            <input
              value={form.username}
              onChange={(e) =>
                setForm({ ...form, username: e.target.value })
              }
              style={{ width: "100%", marginBottom: "10px" }}
            />

            <label>Bio:</label>
            <textarea
              value={form.bio}
              onChange={(e) => setForm({ ...form, bio: e.target.value })}
              style={{
                width: "100%",
                height: "80px",
                marginBottom: "10px",
              }}
            />

            <label>Profile Picture URL:</label>
            <input
              value={form.profile_picture}
              onChange={(e) =>
                setForm({ ...form, profile_picture: e.target.value })
              }
              style={{ width: "100%", marginBottom: "10px" }}
            />

            <button
              style={{
                padding: "8px 14px",
                background: "#4caf50",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                marginRight: "10px",
              }}
              onClick={handleUpdate}
            >
              Save
            </button>

            <button
              style={{
                padding: "8px 14px",
                background: "#888",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
              }}
              onClick={() => setEditMode(false)}
            >
              Cancel
            </button>
          </>
        )}
      </div>

      {/* MY MADLIBS SECTION */}
      <div style={{ marginTop: "40px", maxWidth: "800px" }}>
        <h2>All My Madlibs ({madlibs.length})</h2>

        {madlibsLoading ? (
          <p>Loading your madlibs...</p>
        ) : madlibs.length === 0 ? (
          <p style={{ color: "#666" }}>You haven't created any madlibs yet.</p>
        ) : (
          <div style={{ display: "grid", gap: "15px", marginTop: "20px" }}>
            {madlibs.map((madlib) => {
              const template = templates[madlib.template_id];
              const isExpanded = expandedMadlibs[madlib._id];
              const likeCount = likeCounts[madlib._id] ?? 0; // NEW: Get like count
              
              return (
                <div
                  key={madlib._id}
                  style={{
                    border: "1px solid #ddd",
                    borderRadius: "8px",
                    padding: "15px",
                    backgroundColor: "#f9f9f9",
                  }}
                >
                  <div style={{ marginBottom: "10px" }}>
                    <strong style={{ fontSize: "18px", color: "#333" }}>
                      {template?.title || "Loading..."}
                    </strong>
                  </div>
                  
                  <div style={{ marginBottom: "10px", fontSize: "14px", color: "#666" }}>
                    Created: {new Date(madlib.created_at).toLocaleDateString()} at{" "}
                    {new Date(madlib.created_at).toLocaleTimeString()}
                  </div>

                  {/* NEW: Show like count */}
                  <div 
                    style={{ 
                      marginBottom: "15px", 
                      fontSize: "16px", 
                      display: "flex", 
                      alignItems: "center",
                      gap: "8px"
                    }}
                  >
                    <span style={{ fontSize: "20px" }}>❤️</span>
                    <span style={{ fontWeight: "500", color: "#333" }}>
                      {likeCount} {likeCount === 1 ? 'like' : 'likes'}
                    </span>
                  </div>

                  {/* Show/Hide Full Story */}
                  {isExpanded && (
                    <div
                      style={{
                        marginTop: "15px",
                        marginBottom: "15px",
                        padding: "15px",
                        backgroundColor: "#fff",
                        borderRadius: "6px",
                        border: "1px solid #e0e0e0",
                        whiteSpace: "pre-wrap",
                        lineHeight: "1.6",
                      }}
                    >
                      <strong style={{ display: "block", marginBottom: "10px" }}>
                        Your Completed Story:
                      </strong>
                      {template ? renderFilledStory(template, madlib.content) : "Loading story..."}
                    </div>
                  )}

                  {/* Expand/Collapse Button */}
                  <button
                    onClick={() => toggleExpand(madlib._id)}
                    style={{
                      padding: "6px 12px",
                      backgroundColor: "#007bff",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "14px",
                      marginRight: "10px",
                    }}
                  >
                    {isExpanded ? "Hide Story" : "Show Full Story"}
                  </button>

                  <button
                    onClick={() => navigate(`/filled-madlibs/${madlib._id}/comment`)}
                    style={{
                      padding: "6px 12px",
                      backgroundColor: "#5a0fb3",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "14px",
                      marginRight: "10px",
                    }}
                  >
                    View & Comment
                  </button>

                  <button
                    onClick={() => handleDeleteMadlib(madlib._id)}
                    style={{
                      padding: "6px 12px",
                      backgroundColor: "#d11a2a",
                      color: "white",
                      border: "none",
                      borderRadius: "6px",
                      cursor: "pointer",
                      fontSize: "14px",
                    }}
                  >
                    Delete
                  </button>

                  {/* Show image if exists */}
                  {madlib.image_url && (
                    <div style={{ marginTop: "15px" }}>
                      <img
                        src={madlib.image_url}
                        alt="Madlib visualization"
                        style={{
                          maxWidth: "100%",
                          height: "auto",
                          borderRadius: "8px",
                        }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}