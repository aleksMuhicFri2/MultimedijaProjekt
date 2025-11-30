// frontend/src/App.jsx
import { useState, useEffect } from "react";
import SloveniaMap from "./components/SloveniaMap";

import goldMedal from "./images/goldMedal.png";
import silverMedal from "./images/silverMedal.png";
import bronzeMedal from "./images/bronzeMedal.png";

// Only medal regions get icons.
// Everyone else gets: nothing.
const regionIcons = {
  "obalno-kraska": goldMedal,
  "notranjsko-kraska": silverMedal,
  "goriska": bronzeMedal,
};

function App() {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [regionData, setRegionData] = useState(null);
  const [regionError, setRegionError] = useState(null);

  useEffect(() => {
    if (!selectedRegion) {
      setRegionData(null);
      setRegionError(null);
      return;
    }

    const fetchRegion = async () => {
      try {
        const res = await fetch(
          `http://localhost:5000/api/region/${selectedRegion}`
        );

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          setRegionData(null);
          setRegionError(err.error || "Unknown error");
          return;
        }

        const data = await res.json();
        setRegionData(data);
        setRegionError(null);
      } catch (err) {
        console.error("Region fetch failed:", err);
        setRegionData(null);
        setRegionError("Cannot reach backend");
      }
    };

    fetchRegion();
  }, [selectedRegion]);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col items-center p-8 gap-8">
      <h1 className="text-5xl font-bold tracking-tight">
        KJE JE NAJBOLJSE
      </h1>

      <p className="text-slate-600">
        Click on a region to select it. Later this will show data from the backend.
      </p>

      <SloveniaMap
        selectedRegion={selectedRegion}
        onRegionSelect={setSelectedRegion}
        regionIcons={regionIcons}
      />

      <div className="mt-4 flex flex-col gap-3">
        {selectedRegion ? (
          <div className="px-4 py-2 rounded-lg bg-white shadow">
            Selected region:{" "}
            <span className="font-semibold">{selectedRegion}</span>
          </div>
        ) : (
          <div className="px-4 py-2 rounded-lg bg-white shadow text-slate-500">
            No region selected yet.
          </div>
        )}

        {selectedRegion && (
          <div className="px-4 py-3 rounded-lg bg-white shadow text-sm text-slate-700">
            {regionError && (
              <div className="text-red-500">
                Could not load data: {regionError}
              </div>
            )}

            {!regionError && !regionData && (
              <div className="text-slate-400">Loading region data...</div>
            )}

            {regionData && (
              <div className="space-y-1">
                <div>
                  <span className="font-semibold">Salary:</span>{" "}
                  {regionData.salary}
                </div>
                <div>
                  <span className="font-semibold">Housing:</span>{" "}
                  {regionData.housing}
                </div>
                <div>
                  <span className="font-semibold">Pollution:</span>{" "}
                  {regionData.pollution}
                </div>
                <div>
                  <span className="font-semibold">Health:</span>{" "}
                  {regionData.health}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
    
  );
}

export default App;
