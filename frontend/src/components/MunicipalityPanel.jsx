import React from "react";

function MunicipalityPanel({ data }) {
  const getWeatherColor = (score) => {
    if (score >= 8) return "#2e7d32";
    if (score >= 6) return "#66bb6a";
    if (score >= 4) return "#fbc02d";
    return "#d32f2f";
  };

  // Helper to color-code the demographic tag
  const getTagStyle = (tag) => {
    const styles = {
      "Mlado Prebivalstvo": { bg: "#e8f5e9", text: "#2e7d32", border: "#c8e6c9" },
      "Delavno Prebivalstvo": { bg: "#e3f2fd", text: "#1565c0", border: "#bbdefb" },
      "Staro Prebivalstvo": { bg: "#fff3e0", text: "#e65100", border: "#ffe0b2" }
    };
    return styles[tag] || { bg: "#f5f5f5", text: "#616161", border: "#e0e0e0" };
  };

  const tagStyle = getTagStyle(data.main_demographic);

  return (
    <div style={{
        display: "flex", flexDirection: "row", justifyContent: "space-between",
        width: "100%", maxWidth: "1300px", padding: "1.5rem",
        backgroundColor: "#fff", borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.08)", gap: "1.5rem", fontFamily: "sans-serif"
    }}>
      {/* SECTION 1: Location & Demographic Tag */}
      <div style={{ flex: 1.2, textAlign: "left" }}>
        <h2 style={{ margin: "0 0 0.2rem 0", color: "#333" }}>{data.name}</h2>
        <p style={{ margin: "0 0 0.8rem 0", color: "#666", fontSize: "0.9rem" }}>{data.region}</p>
        
        {/* THE NEW TAG */}
        <div style={{
          display: "inline-block", padding: "4px 12px", borderRadius: "20px",
          backgroundColor: tagStyle.bg, color: tagStyle.text,
          border: `1px solid ${tagStyle.border}`, fontSize: "0.75rem", fontWeight: "bold",
          textTransform: "uppercase", letterSpacing: "0.5px"
        }}>
          🏷️ {data.main_demographic ?? "Calculating..."}
        </div>

        <div style={{ marginTop: "1.5rem" }}>
          <span style={{ fontSize: "0.7rem", color: "#999", textTransform: "uppercase" }}>Weather Index</span>
          <div style={{ fontSize: "2.2rem", fontWeight: "bold", color: getWeatherColor(data.weather_index) }}>
            {data.weather_index?.toFixed(1) ?? "N/A"}
            <span style={{ fontSize: "0.9rem", color: "#ccc" }}> / 10</span>
          </div>
        </div>
      </div>

      {/* SECTION 2: Population */}
      <div style={{ flex: 1 }}>
        <h4 style={{ borderBottom: "2px solid #f0f0f0", paddingBottom: "5px", color: "#444" }}>👥 Population</h4>
        <div style={{ fontSize: "0.9rem", lineHeight: "1.8" }}>
          <div>Young: <b>{data.population_young.toLocaleString()}</b></div>
          <div>Working: <b>{data.population_working.toLocaleString()}</b></div>
          <div>Old: <b>{data.population_old.toLocaleString()}</b></div>
        </div>
      </div>

      {/* SECTION 3: Real Estate */}
      <div style={{ flex: 1 }}>
        <h4 style={{ borderBottom: "2px solid #f0f0f0", paddingBottom: "5px", color: "#444" }}>🏠 Real Estate</h4>
        <div style={{ fontSize: "0.9rem", lineHeight: "1.8" }}>
          <div>Apartment: <b>{data.avg_price_m2_apartment ? `${data.avg_price_m2_apartment}€` : "N/A"}</b></div>
          <div>Rent (m²): <b>{data.avg_rent_m2 ? `${data.avg_rent_m2}€` : "N/A"}</b></div>
        </div>
      </div>

      {/* SECTION 4: Health & Environment */}
      <div style={{ flex: 1 }}>
        <h4 style={{ borderBottom: "2px solid #f0f0f0", paddingBottom: "5px", color: "#444" }}>🏥 Quality of Life</h4>
        <div style={{ fontSize: "0.9rem", lineHeight: "1.8" }}>
          <div>Health Coverage: <b>{(data.ioz_ratio * 100).toFixed(1)}%</b></div>
          <div>Air (AQI): <b style={{ color: data.history_avg_aqi > 35 ? "#ef6c00" : "#2e7d32" }}>{data.history_avg_aqi.toFixed(1)}</b></div>
          <div>Sun Days: <b>{data.history_sunny_days}</b></div>
        </div>
      </div>
    </div>
  );
}

export default MunicipalityPanel;