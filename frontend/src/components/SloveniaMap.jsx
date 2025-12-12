import React, { useEffect, useState, useCallback } from "react";
import { parseSloveniaSvg } from "../utils/ParseSloveniaSvg";

const COLOR_DEFAULT = "white";
const COLOR_HOVER = "#93c5fd";    // light blue
const COLOR_SELECTED = "#2563eb"; // strong blue

function SloveniaMap({ selectedCode, onSelectMunicipality }) {
  const [municipalities, setMunicipalities] = useState([]);
  const [hoveredCode, setHoveredCode] = useState(null);

  useEffect(() => {
    fetch("/SloveniaMap.svg")
      .then((res) => res.text())
      .then((svgText) => setMunicipalities(parseSloveniaSvg(svgText)))
      .catch(console.error);
  }, []);

  const getFillColor = (code) => {
    if (code === selectedCode) return COLOR_SELECTED;
    if (code === hoveredCode) return COLOR_HOVER;
    return COLOR_DEFAULT;
  };

  const handleClick = useCallback(
    (code) => () => onSelectMunicipality(code),
    [onSelectMunicipality]
  );

  return (
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
            fill={getFillColor(m.code)}
            stroke="black"
            strokeWidth={100}
            onMouseEnter={() => setHoveredCode(m.code)}
            onMouseLeave={() => setHoveredCode(null)}
            onClick={handleClick(m.code)}
            style={{ cursor: "pointer", transition: "fill 0.15s ease" }}
          />
        ))
      )}
    </svg>
  );
}

export default SloveniaMap;
