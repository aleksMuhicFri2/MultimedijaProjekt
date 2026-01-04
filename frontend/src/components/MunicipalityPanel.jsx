import React from "react";
import MunicipalityGraphs from "./MunicipalityGraphs";

function MunicipalityPanel({ data }) {
  if (!data) {
    return <p style={{ textAlign: 'center', color: '#9CA3AF', padding: '2rem' }}>No data available</p>;
  }

  const displayValue = (value, suffix = '') => {
    if (value === null || value === undefined || value === '') {
      return 'N/A';
    }
    if (typeof value === 'number') {
      return `${value.toLocaleString('sl-SI')}${suffix}`;
    }
    return `${value}${suffix}`;
  };

  return (
    <div style={{ width: "100%", animation: "fadeIn 0.5s ease-out" }}>
      <h2 style={{ 
        fontSize: "1.75rem", 
        fontWeight: 700, 
        color: "#1F2933",
        marginBottom: "1.5rem",
        paddingBottom: "0.75rem",
        borderBottom: "2px solid #E5E7EB"
      }}>
        {data.name || 'Unknown Municipality'}
      </h2>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        {/* Basic Info */}
        <div>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "#374151", marginBottom: "0.75rem" }}>
            Basic Information
          </h3>
          <p style={itemStyle}><strong>Code:</strong> {displayValue(data.code)}</p>
          <p style={itemStyle}><strong>Region:</strong> {displayValue(data.region)}</p>
          <div style={itemStyle}>
            <strong>Population:</strong>
            <div style={{ marginLeft: '1rem', marginTop: '0.5rem' }}>
              <div><strong>Young:</strong> {displayValue(data.population_young)}</div>
              <div><strong>Working:</strong> {displayValue(data.population_working)}</div>
              <div><strong>Old:</strong> {displayValue(data.population_old)}</div>
            </div>
          </div>
        </div>

        {/* Real Estate - Apartments */}
        <div>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "#374151", marginBottom: "0.75rem" }}>
            Apartments
          </h3>
          <p style={itemStyle}>
            <strong>Avg Price/m²:</strong> {displayValue(data.avg_price_m2_apartment, ' €')}
          </p>
          <p style={itemStyle}>
            <strong>Median Price/m²:</strong> {displayValue(data.median_price_m2_apartment, ' €')}
          </p>
          <p style={itemStyle}>
            <strong>Deals:</strong> {displayValue(data.deals_sale_apartment)}
          </p>
        </div>

        {/* Real Estate - Houses */}
        <div>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "#374151", marginBottom: "0.75rem" }}>
            Houses
          </h3>
          <p style={itemStyle}>
            <strong>Avg Price/m²:</strong> {displayValue(data.avg_price_m2_house, ' €')}
          </p>
          <p style={itemStyle}>
            <strong>Median Price/m²:</strong> {displayValue(data.median_price_m2_house, ' €')}
          </p>
          <p style={itemStyle}>
            <strong>Deals:</strong> {displayValue(data.deals_sale_house)}
          </p>
        </div>

        {/* Rent */}
        <div>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "#374151", marginBottom: "0.75rem" }}>
            Rent
          </h3>
          <p style={itemStyle}>
            <strong>Avg Rent/m²:</strong> {displayValue(data.avg_rent_m2, ' €')}
          </p>
          <p style={itemStyle}>
            <strong>Median Rent/m²:</strong> {displayValue(data.median_rent_m2, ' €')}
          </p>
          <p style={itemStyle}>
            <strong>Deals:</strong> {displayValue(data.deals_rent)}
          </p>
        </div>

        {/* Health Insurance (IOZ) */}
        {(data.ioz_ratio || data.insured_total) && (
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "#374151", marginBottom: "0.75rem" }}>
              Health Insurance
            </h3>
            {data.ioz_ratio && (
              <p style={itemStyle}>
                <strong>IOZ Coverage:</strong> {displayValue((data.ioz_ratio * 100).toFixed(2), '%')}
              </p>
            )}
            {data.insured_total && (
              <p style={itemStyle}>
                <strong>Total Insured:</strong> {displayValue(data.insured_total)}
              </p>
            )}
            {data.insured_with_ioz && (
              <p style={itemStyle}>
                <strong>With IOZ:</strong> {displayValue(data.insured_with_ioz)}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Graphs show here (right panel), once `data` exists */}
      <MunicipalityGraphs data={data} />

      {/* Debug Panel */}
      <details style={{ marginTop: '1.5rem', fontSize: '0.75rem', color: '#6B7280' }}>
        <summary style={{ cursor: 'pointer', padding: '0.5rem', background: '#F3F4F6', borderRadius: '8px' }}>
          Debug: Raw API Data
        </summary>
        <pre style={{ 
          background: '#F9FAFB', 
          padding: '1rem', 
          borderRadius: '8px',
          overflow: 'auto',
          maxHeight: '200px',
          marginTop: '0.5rem',
          border: '1px solid #E5E7EB'
        }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
}

const itemStyle = {
  fontSize: "0.95rem",
  color: "#1F2933",
  marginBottom: "0.5rem",
  lineHeight: "1.6"
};

export default MunicipalityPanel;