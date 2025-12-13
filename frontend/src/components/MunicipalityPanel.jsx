function MunicipalityPanel({ data }) {
  return (
    <div>
      <h2>{data.name}</h2>
      <p>
        <b>Region:</b> {data.region ?? "N/A"}
      </p>

      <h3>Population</h3>
      <ul>
        <li>Young: {data.population_young ?? "N/A"}</li>
        <li>Working: {data.population_working ?? "N/A"}</li>
        <li>Old: {data.population_old ?? "N/A"}</li>
      </ul>

      <h3>Prices</h3>
      <ul>
        <li>Apartment €/m²: {data.avg_price_m2_apartment ?? "N/A"}</li>
        <li>House €/m²: {data.avg_price_m2_house ?? "N/A"}</li>
        <li>Rent €/m²: {data.avg_rent_m2 ?? "N/A"}</li>
      </ul>

      <h3>Health insurance (IOZ)</h3>
      <ul>
        <li>
          IOZ coverage:{" "}
          {data.ioz_ratio != null
            ? `${(data.ioz_ratio * 100).toFixed(1)}%`
            : "N/A"}
        </li>
        <li>Total insured: {data.insured_total ?? "N/A"}</li>
        <li>With IOZ: {data.insured_with_ioz ?? "N/A"}</li>
        <li>Without IOZ: {data.insured_without_ioz ?? "N/A"}</li>
      </ul>
    </div>
  );
}

export default MunicipalityPanel;