import React, { useEffect, useState, useCallback } from "react";
import { parseSloveniaSvg } from "../utils/ParseSloveniaSvg";

/* --------------------------------------------------
   Region → base blue color
-------------------------------------------------- */
const REGION_COLORS = {
  gorenjska: "#4F83CC",
  goriska: "#5C9DED",
  "obalno-kraska": "#3A7CA5",
  "notranjsko-kraska": "#6BAED6",
  osrednjeslovenska: "#2F6DAE",
  zasavska: "#4A90E2",
  savinjska: "#5DA9E9",
  koroska: "#3F88C5",
  podravska: "#6CA6CD",
  pomurska: "#7FB3D5",
  posavska: "#5B8DB8",
  jugovzhodna: "#4C72B0",
};

const FALLBACK_COLOR = "#e5e7eb";

function SloveniaMap({ selectedCode, onSelectMunicipality }) {
  const [municipalities, setMunicipalities] = useState([]);
  const [hoveredCode, setHoveredCode] = useState(null);
  const [regionByCode, setRegionByCode] = useState({});

  /* -----------------------------------------
     Load regions (CODE → REGION)
  ----------------------------------------- */
  useEffect(() => {
    fetch("http://localhost:5000/api/municipalities/regions")
      .then((res) => res.json())
      .then(setRegionByCode)
      .catch(console.error);
  }, []);

  /* -----------------------------------------
     Load SVG + join by CODE
  ----------------------------------------- */
  useEffect(() => {
    if (!Object.keys(regionByCode).length) return;

    fetch("/SloveniaMap.svg")
      .then((res) => res.text())
      .then((svgText) => {
        const parsed = parseSloveniaSvg(svgText);

        setMunicipalities(
          parsed.map((m) => ({
            ...m,
            region: regionByCode[m.code],
          }))
        );
      })
      .catch(console.error);
  }, [regionByCode]);

  const handleClick = useCallback(
    (code) => () => onSelectMunicipality(code),
    [onSelectMunicipality]
  );

  return (
    <>
      <svg
        viewBox="375000 -200000 250000 180000"
        preserveAspectRatio="xMidYMid meet"
        style={{ width: "50%", height: "auto" }}
      >
        {municipalities.flatMap((m) =>
          m.dList.map((d, i) => (
            <path
              key={`${m.code}-${i}`}
              d={d}
              fill={REGION_COLORS[m.region] ?? FALLBACK_COLOR}
              stroke="#ffffff"
              strokeWidth={20}
              className="municipality"
              data-hovered={m.code === hoveredCode}
              data-selected={m.code === selectedCode}
              onMouseEnter={() => setHoveredCode(m.code)}
              onMouseLeave={() => setHoveredCode(null)}
              onClick={handleClick(m.code)}
            />
          ))
        )}
      </svg>

      <style>{`
        .municipality {
          cursor: pointer;
          transition: filter 0.15s ease;
        }

        .municipality[data-hovered="true"]:not([data-selected="true"]) {
          filter: brightness(1.12);
        }

        .municipality[data-selected="true"] {
          filter: brightness(1.5);
        }
      `}</style>
    </>
  );
}

export default SloveniaMap;
