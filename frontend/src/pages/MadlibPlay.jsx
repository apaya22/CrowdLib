import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getCSRFToken } from "../config";

const API_ROOT = "http://localhost:8000/api";

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
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

export default function MadlibPlay() {
  const { id } = useParams(); // template id from /madlibs/:id
  const navigate = useNavigate();
  const [generatedImage, setGeneratedImage] = useState(null);
  const [template, setTemplate] = useState(null);
  const [values, setValues] = useState({});
  const [me, setMe] = useState(null);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saveStatus, setSaveStatus] = useState("");

  // load current user (for saving)
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_ROOT}/users/profile/`, { credentials: "include" });
        if (r.ok) setMe(await r.json());
      } catch (err) {
        console.error("error obtaining pf: ", err);
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
        const data = await r.json();
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

  // run & generate the madlib
async function onSubmit(e) {
  e.preventDefault();
  setError("");

  const filled = renderStory(template.template, values);
  setResult(filled);

  // Clear previous image
  setGeneratedImage(null);

  // Check if user is logged in
  if (!me?._id) {
    alert("You must be logged in to generate images.");
    return;
  }

  try {
    const inputted_blanks = Object.entries(values).map(([k, v]) => ({
      id: String(k),
      input: String(v),
    }));

    const csrftoken = getCSRFToken();

    // STEP 1: Save the madlib first to get a real ID
    console.log("Saving madlib...");
    const saveRes = await fetch(`${API_ROOT}/madlibs/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({
        template_id: String(id),
        creator_id: String(me._id),
        inputted_blanks,
      }),
    });

    if (!saveRes.ok) {
      const txt = await saveRes.text().catch(() => "");
      console.warn("Save failed:", saveRes.status, txt);
      alert("Failed to save madlib.");
      return;
    }

    const saveData = await saveRes.json();
    const realMadlibId = saveData.id; // Get the real madlib ID from response
    console.log("Madlib saved with ID:", realMadlibId);

    // STEP 2: Generate image using the real madlib ID
    console.log("Generating image...");
    const imgRes = await fetch(`${API_ROOT}/image-gen/generate/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({
        madlib_id: realMadlibId,  // Use the real ID now
        madlib_text: filled,
        extra_prompt_args: {
          style: "watercolor painting",
          aspect_ratio: "1:1",
        },
      }),
    });

    if (!imgRes.ok) {
      console.error("Image generation error:", await imgRes.text());
      alert("Failed to generate image, but madlib was saved!");
      return;
    }

    const imgData = await imgRes.json();
    console.log("Generated image URL:", imgData.url);

    // Display the generated image
    setGeneratedImage(imgData.url || null);
    setSaveStatus("Saved with image!");
    
  } catch (err) {
    console.error("Error:", err);
    alert("An error occurred.");
  }
}

// Update the onSave function to avoid duplicate saves
async function onSave() {
  alert("Your madlib is already saved! Generate button saves automatically.");
}


  // separate Save button logic
  async function onSave() {
    setSaveStatus("");

    if (!me?._id) {
      setSaveStatus("You must be logged in to save.");
      return;
    }

    try {
      const inputted_blanks = Object.entries(values).map(([k, v]) => ({
        id: String(k),
        input: String(v),
      }));



      console.log(me._id);
      //console.log(csrftoken);

      //SAVE 
      const csrftoken = getCSRFToken();
      console.log("HEADER TOKEN:", getCSRFToken());
      console.log("COOKIE TOKEN:", document.cookie);

      console.log(`${API_ROOT}/madlibs/create/`)
      const res = await fetch(`${API_ROOT}/madlibs/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,

        },
        body: JSON.stringify({
          template_id: String(id),
          creator_id: String(me._id),
          inputted_blanks,
        }),
      });
      
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        console.warn("Save failed:", res.status, txt);
        setSaveStatus("Save failed.");
        return;
      }
      else{
        console.log("Saved");
      }
      setSaveStatus("Saved!");
    } catch (err) {
      console.error("Save error:", err);
      setSaveStatus("Save failed.");
    }
  }
    // delete templates
    async function handleDeleteTemplate() {
    if (!me?._id) {
      alert("You must be logged in to delete templates.");
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete this template? This cannot be undone."
    );
    if (!confirmed) return;

    try {
      const csrftoken = getCSRFToken();

      const res = await fetch(`${API_ROOT}/templates/${id}/`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrftoken,
        },
      });

      if (res.status === 204 || res.status === 200) {
        alert("Template deleted.");
        // change this route to wherever you list templates
        navigate("/"); 
      } else {
        const txt = await res.text().catch(() => "");
        console.error("Delete failed:", res.status, txt);
        alert("Failed to delete template.");
      }
    } catch (err) {
      console.error("Delete error:", err);
      alert("An error occurred while deleting the template.");
    }
  }

  // states
  if (loading) return <main style={{ padding: "2rem" }}>Loading…</main>;
  if (error) return <main style={{ padding: "2rem", color: "red" }}>{error}</main>;
  if (!template) return <main style={{ padding: "2rem" }}>Not found.</main>;

  return (
    <main
  style={{
    maxWidth: 500,
    margin: "2rem auto",
    padding: "1.5rem",
    background: "#fafafa",
    borderRadius: 12,
    border: "1px solid #e5e5e5",
    boxShadow: "0 2px 6px rgba(0,0,0,0.06)",
  }}
>
  <header
  style={{
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "0.75rem",
    marginBottom: "1rem",
  }}
>
  <h1 style={{ margin: 0, fontSize: "1.5rem" }}>
    {template.title || "Untitled"}
  </h1>

  {/* show delete button if logged in */}
  {me?._id && (
    <button
      type="button"
      onClick={handleDeleteTemplate}
      style={{
        padding: "0.4rem 0.8rem",
        borderRadius: 8,
        border: "none",
        cursor: "pointer",
        backgroundColor: "#e11d48",
        color: "#fff",
        fontSize: "0.9rem",
        fontWeight: 600,
        whiteSpace: "nowrap",
      }}
    >
      Delete
    </button>
  )}
</header>


  {(template.blanks?.length ?? 0) === 0 ? (
    <p style={{ whiteSpace: "pre-wrap", marginTop: "1rem" }}>
      {template.template || template.story || "No story provided."}
    </p>
  ) : (
    <form
      onSubmit={onSubmit}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        marginTop: "1rem",
      }}
    >
      {(template.blanks || []).map((b) => {
        const label =
          b.label ||
          b.prompt ||
          b.hint ||
          b.wordType ||
          b.type ||
          (b.placeholder &&
          b.placeholder.toLowerCase() !== "blank"
            ? b.placeholder
            : null) ||
          `Blank #${b.id}`;

        const ph =
          b.placeholder && b.placeholder.toLowerCase() !== "blank"
            ? b.placeholder
            : label;

        return (
          <label
            key={b.id}
            style={{
              display: "flex",
              flexDirection: "column",
              fontSize: "0.9rem",
            }}
          >
            <span style={{ marginBottom: 4, opacity: 0.75 }}>{label}</span>

            <input
              value={values[String(b.id)] ?? ""}
              onChange={(e) =>
                setValues((v) => ({
                  ...v,
                  [String(b.id)]: e.target.value,
                }))
              }
              placeholder={ph}
              autoComplete="off"
              required
              style={{
                padding: "0.55rem 0.75rem",
                border: "1px solid #ccc",
                borderRadius: 6,
                fontSize: "0.95rem",
              }}
            />
          </label>
        );
      })}

      <button
        type="submit"
        style={{
          marginTop: "0.5rem",
          padding: "0.6rem",
          borderRadius: 8,
          fontSize: "1rem",
          background: "#28a745",
          color: "white",
          border: "none",
          cursor: "pointer",
        }}
      >
        Generate
      </button>
    </form>
  )}

{result && (
  <section
    style={{
      marginTop: "2rem",
      padding: "1rem",
      border: "1px solid #ddd",
      borderRadius: 10,
      background: "white",
    }}
  >
    <h3>Result</h3>
    <p style={{ whiteSpace: "pre-wrap" }}>{result}</p>

    {generatedImage && (
      <img
        src={generatedImage}
        alt="Generated illustration"
        style={{
          width: "100%",
          maxWidth: "600px",
          borderRadius: "10px",
          marginTop: "1rem",
        }}
      />
    )}

    <button
  type="submit"
  style={{
    marginTop: "0.5rem",
    padding: "0.6rem",
    borderRadius: 8,
    fontSize: "1rem",
    background: "#28a745",
    color: "white",
    border: "none",
    cursor: "pointer",
  }}
>
  Save & Generate Image
</button>

    {saveStatus && (
      <p style={{ marginTop: "0.5rem", color: "#555" }}>{saveStatus}</p>
    )}
    </section>
  )}

  </main>
  );
}
