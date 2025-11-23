//Local call
export const BACKEND = "http://localhost:8000";

export function getCSRFToken() {
  const name = "csrftoken=";
  const decoded = decodeURIComponent(document.cookie);
  const parts = decoded.split(";");

  for (let p of parts) {
    let c = p.trim();
    if (c.startsWith(name)) {
      return c.substring(name.length, c.length);
    }
  }
  return null;
}