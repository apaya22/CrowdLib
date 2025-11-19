import { useEffect, useState } from "react";
import { BACKEND } from "../config";

// Get CSRF cookie
function getCookie(name) {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith(name + "="));
  return cookieValue ? cookieValue.split("=")[1] : null;
}

export default function Profile() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  {/* fetch profile */}
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

  {/* delete account */}
  async function handleDeleteAccount() {
    const csrf = getCookie("csrftoken");

    if (!csrf) {
      alert("Missing CSRF token.");
      return;
    }

    try {
      const res = await fetch(`${BACKEND}/api/users/delete/`, {
        method: "POST",
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


{/* Handler Update */}
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
 
{/* Render */}
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
    </div>
  );
}
