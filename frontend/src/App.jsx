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
      <h1 style={{ margin: "0.5rem", textAlign: "center" }}>
        Slovenian Municipalities
      </h1>

      {/* MAP – TOP (Takes remaining space) */}
      <div
        style={{
          flex: 1,
          width: "100%",
          display: "flex",
          // Align content to the right
          justifyContent: "flex-end", 
          // Center it vertically within the top space
          alignItems: "center",       
          position: "relative",
          paddingRight: "50px", // A little breathing room from the right edge
          boxSizing: "border-box"
        }}
      >
        {/* Map Wrapper: Takes up ~2/3 (60-65%) of the width */}
        <div style={{ width: "40%" }}>
          <SloveniaMap
            selectedCode={selectedCode}
            onSelectMunicipality={setSelectedCode}
          />
        </div>
      </div>

      {/* DATA PANEL – BOTTOM */}
      <div
        style={{
          height: "30vh",
          width: "100%",
          borderTop: "2px solid #ccc",
          backgroundColor: "#f9f9f9",
          overflowY: "auto",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        {loading && <p>Loading data...</p>}
        {!data && !loading && <p style={{ color: "#666" }}>Select a municipality on the map</p>}
        {data && <MunicipalityPanel data={data} />}
      </div>
    </div>
  );
}

export default App;