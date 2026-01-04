import React, { useMemo } from "react";
import "chart.js/auto";
import { Bar, Doughnut } from "react-chartjs-2";

function isNumber(x) {
  return typeof x === "number" && Number.isFinite(x);
}

function toNumberOrNull(x) {
  if (x === null || x === undefined || x === "") return null;
  const n = typeof x === "string" ? Number(x) : x;
  return Number.isFinite(n) ? n : null;
}

export default function MunicipalityGraphs({ data }) {
  const population = useMemo(() => {
    const young = toNumberOrNull(data?.population_young);
    const working = toNumberOrNull(data?.population_working);
    const old = toNumberOrNull(data?.population_old);

    const ok = [young, working, old].every(isNumber) && (young + working + old) > 0;

    return {
      ok,
      chartData: {
        labels: ["0–14", "15–64", "65+"],
        datasets: [{
          label: "Population",
          data: [young, working, old],
          backgroundColor: ["#60a5fa", "#34d399", "#f59e0b"],
          borderColor: "#ffffff",
          borderWidth: 2,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
          title: { display: true, text: "Population by age group" },
          tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.raw?.toLocaleString?.("sl-SI") ?? ctx.raw}` } },
        },
      },
    };
  }, [data]);

  const prices = useMemo(() => {
    const entries = [
      { label: "Apartment (€/m²)", avg: toNumberOrNull(data?.avg_price_m2_apartment), med: toNumberOrNull(data?.median_price_m2_apartment) },
      { label: "House (€/m²)", avg: toNumberOrNull(data?.avg_price_m2_house), med: toNumberOrNull(data?.median_price_m2_house) },
      { label: "Rent (€/m²)", avg: toNumberOrNull(data?.avg_rent_m2), med: toNumberOrNull(data?.median_rent_m2) },
    ].filter(e => isNumber(e.avg) || isNumber(e.med));

    const labels = entries.map(e => e.label);
    const avgValues = entries.map(e => e.avg ?? null);
    const medValues = entries.map(e => e.med ?? null);

    const showMedian = medValues.some(isNumber);
    const ok = entries.length > 0;

    const datasets = [{
      label: "Average",
      data: avgValues,
      backgroundColor: "rgba(59, 130, 246, 0.75)",
    }];

    if (showMedian) {
      datasets.push({
        label: "Median",
        data: medValues,
        backgroundColor: "rgba(16, 185, 129, 0.75)",
      });
    }

    return {
      ok,
      chartData: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" }, title: { display: true, text: "Prices (€/m²)" } },
        scales: { y: { beginAtZero: true } },
      },
    };
  }, [data]);

  const deals = useMemo(() => {
    const entries = [
      { label: "Apartment sales", v: toNumberOrNull(data?.deals_sale_apartment) },
      { label: "House sales", v: toNumberOrNull(data?.deals_sale_house) },
      { label: "Rent deals", v: toNumberOrNull(data?.deals_rent) },
    ].filter(e => isNumber(e.v));

    const ok = entries.length > 0;

    return {
      ok,
      chartData: {
        labels: entries.map(e => e.label),
        datasets: [{
          label: "Deals",
          data: entries.map(e => e.v),
          backgroundColor: ["#93c5fd", "#86efac", "#fdba74"].slice(0, entries.length),
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, title: { display: true, text: "Deal counts" } }, scales: { y: { beginAtZero: true } } },
    };
  }, [data]);

  const cardStyle = {
    border: "1px solid #E5E7EB",
    borderRadius: 12,
    padding: "1rem",
    background: "#fff",
  };

  const gridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: "1rem",
    marginTop: "1.25rem",
  };

  const chartBoxStyle = { height: 260 };

  return (
    <div style={{ marginTop: "1.5rem" }}>
      <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#374151", marginBottom: "0.5rem" }}>
        Graphs
      </h3>

      <div style={gridStyle}>
        <div style={cardStyle}>
          <div style={chartBoxStyle}>
            {population.ok ? (
              <Doughnut data={population.chartData} options={population.options} />
            ) : (
              <p style={{ color: "#6B7280" }}>Not enough population data for a chart.</p>
            )}
          </div>
        </div>

        <div style={cardStyle}>
          <div style={chartBoxStyle}>
            {prices.ok ? (
              <Bar data={prices.chartData} options={prices.options} />
            ) : (
              <p style={{ color: "#6B7280" }}>Not enough price data for a chart.</p>
            )}
          </div>
        </div>

        <div style={cardStyle}>
          <div style={chartBoxStyle}>
            {deals.ok ? (
              <Bar data={deals.chartData} options={deals.options} />
            ) : (
              <p style={{ color: "#6B7280" }}>Not enough deal data for a chart.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
