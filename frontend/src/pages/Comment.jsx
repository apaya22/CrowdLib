import { useParams, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

const API_ROOT = (import.meta.env.VITE_API_BASE || "http://localhost:8000/api").replace(/\/$/, "");

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

export default function Comment() {
  const { id } = useParams();
  const location = useLocation();
  
  const isFilledMadlib = location.pathname.includes("/filled-madlibs/");
  const [commentLikes, setCommentLikes] = useState({});
  const [madlib, setMadlib] = useState(null);
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [comment, setComment] = useState("");
  const [comments, setComments] = useState([]);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const res = await fetch(`${API_ROOT}/users/profile/`, {
          credentials: "include",
        });
        if (res.ok) {
          const user = await res.json();
          setCurrentUser(user);
        }
      } catch (err) {
        console.error("Failed to load user:", err);
      }
    }
    
    loadUser();
  }, []);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);

        if (isFilledMadlib) {
          const madlibRes = await fetch(`${API_ROOT}/madlibs/${id}/`, {
            credentials: "include",
          });

          if (!madlibRes.ok) {
            throw new Error("Failed to load filled madlib");
          }

          const madlibData = await madlibRes.json();
          setMadlib(madlibData);

          const templateRes = await fetch(`${API_ROOT}/templates/${madlibData.template_id}/`, {
            credentials: "include",
          });

          if (!templateRes.ok) {
            throw new Error("Failed to load template");
          }

          const templateData = await templateRes.json();
          setTemplate(templateData);
        } else {
          const res = await fetch(`${API_ROOT}/templates/${id}/`, {
            credentials: "include",
          });

          if (!res.ok) {
            throw new Error("Failed to load template");
          }

          const data = await res.json();
          setTemplate(data);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [id, isFilledMadlib]);
  
  // Load comments
  useEffect(() => {
    async function loadComments() {
      if (!id || !isFilledMadlib) return;
      
      try {
        setCommentsLoading(true);
        
        // CORRECTED: Use /api/posts/{id}/comments/
        const res = await fetch(
          `${API_ROOT}/comments/${id}/comments/`,
          { credentials: "include" }
        );
        
        if (res.ok) {
          const data = await res.json();
          const loadedComments = data.comments || [];
          setComments(loadedComments);
          
          // Load like data for each comment using POST endpoints
          const likesData = {};
          for (const comment of loadedComments) {
            try {
              // Use the COMMENT ID (not post ID) for likes
              const commentId = comment._id;
              
              // CORRECTED: Use /api/likes/{comment_id}/count/
              const countRes = await fetch(
                `${API_ROOT}/likes/${commentId}/count/`,
                { credentials: "include" }
              );
              
              // CORRECTED: Use /api/likes/{comment_id}/liked/
              const likedRes = await fetch(
                `${API_ROOT}/likes/${commentId}/liked/`,
                { credentials: "include" }
              );
              
              const countData = countRes.ok ? await countRes.json() : {};
              const likedData = likedRes.ok ? await likedRes.json() : {};
              
              likesData[commentId] = {
                count: countData.likes_count || 0,
                liked: likedData.liked || false
              };
            } catch (err) {
              console.error(`Failed to load likes for comment ${comment._id}:`, err);
              likesData[comment._id] = { count: 0, liked: false };
            }
          }
          
          setCommentLikes(likesData);
        } else {
          setComments([]);
        }
      } catch (err) {
        console.error("Failed to load comments:", err);
        setComments([]);
      } finally {
        setCommentsLoading(false);
      }
    }
    
    loadComments();
  }, [id, isFilledMadlib]);

  function renderFilledStory() {
    if (!template?.template || !madlib?.content) {
      return "Story not available";
    }

    const blanksMap = {};
    madlib.content.forEach(blank => {
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

  // UPDATED: handleLikeComment to get liked state from commentLikes
  async function handleLikeComment(commentId) {
    const csrfToken = getCookie('csrftoken');
    const currentLikeState = commentLikes[commentId];
    const alreadyLiked = currentLikeState?.liked || false;
    
    // CORRECTED: Use /api/likes/{comment_id}/like/ or /unlike/
    const url = alreadyLiked
      ? `${API_ROOT}/likes/${commentId}/unlike/`
      : `${API_ROOT}/likes/${commentId}/like/`;

    try {
      const res = await fetch(url, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        }
      });

      if (!res.ok) {
        console.error("Failed to toggle comment like:", res.status);
        return;
      }

      // Refresh like data for this specific comment
      const countRes = await fetch(
        `${API_ROOT}/likes/${commentId}/count/`,
        { credentials: "include" }
      );
      
      const likedRes = await fetch(
        `${API_ROOT}/likes/${commentId}/liked/`,
        { credentials: "include" }
      );
      
      if (countRes.ok && likedRes.ok) {
        const countData = await countRes.json();
        const likedData = await likedRes.json();
        
        // Update only this comment's like data
        setCommentLikes(prev => ({
          ...prev,
          [commentId]: {
            count: countData.likes_count || 0,
            liked: likedData.liked || false
          }
        }));
      }
    } catch (err) {
      console.error("Error toggling comment like:", err);
    }
  }

  async function handleSubmitComment() {
    if (!comment.trim()) {
      alert("Please write a comment before submitting.");
      return;
    }

    if (!currentUser?._id) {
      alert("You must be logged in to comment.");
      return;
    }

    if (!isFilledMadlib) {
      alert("Template comments are not yet supported.");
      return;
    }

    try {
      const csrfToken = getCookie('csrftoken');
      
      // CORRECTED: Use /api/posts/{id}/comment/
      const res = await fetch(`${API_ROOT}/comments/${id}/comment/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          text: comment,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        alert(errorData.error || "Failed to post comment. Please try again.");
        return;
      }

      // Reload comments
      const commentsRes = await fetch(
        `${API_ROOT}/comments/${id}/comments/`,
        { credentials: "include" }
      );
      
      if (commentsRes.ok) {
        const data = await commentsRes.json();
        const loadedComments = data.comments || [];
        setComments(loadedComments);
        
        // Reload like data for all comments
        const likesData = {};
        for (const c of loadedComments) {
          try {
            const countRes = await fetch(
              `${API_ROOT}/likes/${c._id}/count/`,
              { credentials: "include" }
            );
            const likedRes = await fetch(
              `${API_ROOT}/likes/${c._id}/liked/`,
              { credentials: "include" }
            );
            
            const countData = countRes.ok ? await countRes.json() : {};
            const likedData = likedRes.ok ? await likedRes.json() : {};
            
            likesData[c._id] = {
              count: countData.likes_count || 0,
              liked: likedData.liked || false
            };
          } catch (err) {
            likesData[c._id] = { count: 0, liked: false };
          }
        }
        
        setCommentLikes(likesData);
      }

      setComment("");
      alert("Comment posted successfully!");
    } catch (err) {
      console.error("Error posting comment:", err);
      alert("Error posting comment. Please try again.");
    }
  }

  if (loading) return <p style={{ padding: "1rem" }}>Loading…</p>;
  if (error) return <p style={{ color: "red", padding: "1rem" }}>{error}</p>;

  return (
    <div style={{ maxWidth: "800px", margin: "2rem auto", padding: "0 1rem" }}>
      <h1 style={{ color: "#5a0fb3" }}>
        {template?.title || "Untitled Madlib"}
      </h1>

      {isFilledMadlib && madlib && (
        <div style={{ marginBottom: "10px", fontSize: "14px", color: "#666" }}>
          Created: {new Date(madlib.created_at).toLocaleDateString()} at{" "}
          {new Date(madlib.created_at).toLocaleTimeString()}
        </div>
      )}

      {isFilledMadlib && madlib && (
        <div
          style={{
            marginTop: "20px",
            marginBottom: "30px",
            padding: "20px",
            backgroundColor: "#f9f9f9",
            borderRadius: "8px",
            border: "1px solid #ddd",
            whiteSpace: "pre-wrap",
            lineHeight: "1.6",
          }}
        >
          <h3 style={{ marginTop: 0, marginBottom: "15px" }}>Completed Story:</h3>
          {renderFilledStory()}
        </div>
      )}

      {!isFilledMadlib && template?.description && (
        <div
          style={{
            marginTop: "20px",
            marginBottom: "30px",
            padding: "20px",
            backgroundColor: "#f9f9f9",
            borderRadius: "8px",
            border: "1px solid #ddd",
          }}
        >
          <p>{template.description}</p>
        </div>
      )}

      {isFilledMadlib && madlib?.image_url && (
        <div style={{ marginBottom: "30px" }}>
          <h3>Generated Image:</h3>
          <img
            src={madlib.image_url}
            alt="Madlib visualization"
            style={{
              maxWidth: "100%",
              height: "auto",
              borderRadius: "8px",
              border: "1px solid #ddd",
            }}
          />
        </div>
      )}

      <h3 style={{ marginTop: "2rem" }}>Leave a comment</h3>
      <p style={{ fontSize: "14px", color: "#666", marginBottom: "10px" }}>
        {isFilledMadlib 
          ? "Share your thoughts on this completed madlib!" 
          : "Share your thoughts on this madlib template!"}
      </p>

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
        onClick={handleSubmitComment}
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

      <div style={{ marginTop: "2rem" }}>
        <h3>Comments ({comments.length})</h3>
        
        {commentsLoading ? (
          <p style={{ color: "#999", fontStyle: "italic" }}>Loading comments...</p>
        ) : comments.length === 0 ? (
          <p style={{ color: "#999", fontStyle: "italic" }}>
            No comments yet. Be the first to comment!
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "15px", marginTop: "15px" }}>
            {comments.map((c) => {
              // UPDATED: Get like data from commentLikes state
              const likeData = commentLikes[c._id] || { count: 0, liked: false };
              
              return (
                <div
                  key={c._id}
                  style={{
                    padding: "15px",
                    backgroundColor: "#f9f9f9",
                    borderRadius: "8px",
                    border: "1px solid #ddd",
                  }}
                >
                  <div style={{ 
                    display: "flex", 
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "8px", 
                    fontSize: "14px", 
                    color: "#666" 
                  }}>
                    <div>
                      <strong>User ID:</strong> {c.user_id}
                      <span style={{ marginLeft: "15px" }}>
                        {new Date(c.created_at).toLocaleDateString()} at{" "}
                        {new Date(c.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    {/* UPDATED: Use likeData from state and pass only commentId */}
                    <button
                      onClick={() => handleLikeComment(c._id)}
                      style={{
                        background: "none",
                        border: "none",
                        cursor: "pointer",
                        fontSize: "1.2rem",
                        display: "flex",
                        alignItems: "center",
                        gap: "5px",
                        color: likeData.liked ? "red" : "#666",
                        padding: "5px 10px",
                        borderRadius: "6px"
                      }}
                    >
                      {likeData.liked ? "❤️" : "🤍"} 
                      <span style={{ fontSize: "16px" }}>{likeData.count}</span>
                    </button>
                  </div>
                  <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{c.text}</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}