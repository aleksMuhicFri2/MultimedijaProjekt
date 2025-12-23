import React from "react";

function MunicipalityPanel({ data }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-evenly", // Spreads items across the width
        alignItems: "flex-start",
        width: "100%",
        maxWidth: "1200px", // Prevents it from getting too wide on huge screens
        padding: "1rem",
        gap: "2rem",
      }}
    >
      {/* SECTION 1: Header Info */}
      <div style={{ textAlign: "center", minWidth: "200px" }}>
        <h2 style={{ marginTop: 0, marginBottom: "0.5rem" }}>{data.name}</h2>
        <p style={{ margin: 0, color: "#555" }}>
          <b>Region:</b> {data.region ?? "N/A"}
        </p>
      </div>

      {/* SECTION 2: Population */}
      <div>
        <h3 style={{ borderBottom: "1px solid #ddd", paddingBottom: "5px" }}>
          Population
        </h3>
        <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
          <li>Young: {data.population_young ?? "N/A"}</li>
          <li>Working: {data.population_working ?? "N/A"}</li>
          <li>Old: {data.population_old ?? "N/A"}</li>
        </ul>
      </div>

      {/* SECTION 3: Prices */}
      <div>
        <h3 style={{ borderBottom: "1px solid #ddd", paddingBottom: "5px" }}>
          Prices (€/m²)
        </h3>
        <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
          <li>Apartment: {data.avg_price_m2_apartment ?? "N/A"}</li>
          <li>House: {data.avg_price_m2_house ?? "N/A"}</li>
          <li>Rent: {data.avg_rent_m2 ?? "N/A"}</li>
        </ul>
      </div>

      {/* SECTION 4: Health (IOZ) */}
      <div>
        <h3 style={{ borderBottom: "1px solid #ddd", paddingBottom: "5px" }}>
          Health Insurance
        </h3>
        <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
          <li>
            Coverage:{" "}
            {data.ioz_ratio != null
              ? `${(data.ioz_ratio * 100).toFixed(1)}%`
              : "N/A"}
          </li>
          <li>Total: {data.insured_total ?? "N/A"}</li>
          <li>With IOZ: {data.insured_with_ioz ?? "N/A"}</li>
        </ul>
      </div>
    </div>
  );
}

export default MunicipalityPanel;