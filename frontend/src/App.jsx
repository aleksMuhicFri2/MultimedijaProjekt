import React, { useEffect, useState } from "react";
import SloveniaMap from "./components/SloveniaMap";
import MunicipalityPanel from "./components/MunicipalityPanel";

function App() {
  const [selectedCode, setSelectedCode] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedCode) return;

    setLoading(true);
    setData(null);

    fetch(`http://localhost:5000/api/municipality/${selectedCode}`)
      .then((r) => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [selectedCode]);

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* TITLE */}
      <h1
        style={{
          margin: "0.5rem",
          textAlign: "center",
        }}
      >
        Slovenian Municipalities
      </h1>

      {/* MAIN CONTENT */}
      <div
        style={{
          display: "flex",
          flex: 1,
          overflow: "hidden",
        }}
      >
        {/* DATA PANEL – LEFT */}
        <div
          style={{
            width: "350px",
            padding: "1rem",
            overflowY: "auto",
            borderRight: "1px solid #ccc",
          }}
        >
          {loading && <p>Loading…</p>}
          {data && <MunicipalityPanel data={data} />}
          {!data && !loading && <p>Click a municipality</p>}
        </div>

        {/* MAP – RIGHT */}
        <div
          style={{
            flex: 1,
            overflow: "hidden",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <SloveniaMap
            selectedCode={selectedCode}
            onSelectMunicipality={setSelectedCode}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
