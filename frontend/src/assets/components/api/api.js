const API = "http://localhost:5000/api";

<<<<<<< HEAD
export async function fetchMunicipality(code) {
  const res = await fetch(`${API}/municipality/${code}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchAllMunicipalities() {
  const res = await fetch(`${API}/municipalities/all`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function searchCities(criteria) {
  const res = await fetch(`${API}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(criteria),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
=======
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
>>>>>>> 422758504451562949a3ea51caba1fdac5ede881
  return res.json();
}