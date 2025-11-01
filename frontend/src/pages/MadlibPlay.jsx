import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

// If you added the Vite proxy, use "" and paths like /api/...
const BASE = "http://localhost:8000";

export default function MadlibPlay() {
  const { id } = useParams();

  const [madlib, setMadlib]   = useState(null);
  const [values, setValues]   = useState({});
  const [result, setResult]   = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  //Load madlib definition by id
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${BASE}/api/madlibs/${id}/`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const data = await r.json(); //expects { _id, title, template, blanks, ... }
        setMadlib(data);

        //initialize inputs for each blank (ids are strings: "1","2",...)
        const init = {};
        (data.blanks || []).forEach(b => { init[String(b.id)] = ""; });
        setValues(init);
      } catch (e) {
        setError(e.message || "Failed to load madlib");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);



  //submit to backend to generate the text
  async function onSubmit(e) {
    e.preventDefault();
    try {
      const r = await fetch(`${BASE}/api/madlibs/${id}/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ words: values }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json(); // { title, rendered }
      setResult(data.rendered);
    } catch (e) {
      setError(e.message || "Failed to generate");
    }
  }

  if (loading) return <main style={{padding:"2rem"}}>Loading…</main>;
  if (error)   return <main style={{padding:"2rem", color:"red"}}>Error: {error}</main>;
  if (!madlib) return null;

  return (
    <main style={{maxWidth: 900, margin: "2rem auto", padding: "0 1rem"}}>
      <h1>{madlib.title}</h1>

      {/*Inputs for each blank*/}
      <form onSubmit={onSubmit} style={{display:"grid", gap:"0.75rem", marginTop:"1rem"}}>
        {(madlib.blanks || []).map(b => (
          <label key={b.id} style={{display:"grid", gap:"0.25rem"}}>
            <span style={{opacity:.7}}>{b.wordType}</span>
            <input
              value={values[String(b.id)] ?? ""}
              onChange={e => setValues(v => ({ ...v, [String(b.id)]: e.target.value }))}
              placeholder={b.wordType}
              required
            />
          </label>
        ))}
        <button type="submit">Generate</button>
      </form>

      {/*Show the rendered story from backend*/}
      {result && (
        <section style={{marginTop:"1.5rem", padding:"1rem", border:"1px solid #eee", borderRadius:12}}>
          <h3>Result</h3>
          <p style={{whiteSpace:"pre-wrap"}}>{result}</p>
        </section>
      )}
    </main>
  );
}
