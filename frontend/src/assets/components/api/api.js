const API = "http://localhost:5000/api";

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
  return res.json();
}