const API = "http://localhost:5000/api";

export async function fetchRegion(name) {
  const res = await fetch(`${API}/region/${name}`);
  return res.json();
}

export async function computeScores(weights) {
  const res = await fetch(`${API}/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(weights)
  });
  return res.json();
}