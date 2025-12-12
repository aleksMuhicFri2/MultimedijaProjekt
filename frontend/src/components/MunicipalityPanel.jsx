function MunicipalityPanel({ data }) {
  return (
    <div>
      <h2>{data.name}</h2>
      <p><b>Region:</b> {data.region}</p>

      <h3>Population</h3>
      <ul>
        <li>Young: {data.population_young}</li>
        <li>Working: {data.population_working}</li>
        <li>Old: {data.population_old}</li>
      </ul>

      <h3>Prices</h3>
      <ul>
        <li>Apartment €/m²: {data.avg_price_m2_apartment ?? "N/A"}</li>
        <li>House €/m²: {data.avg_price_m2_house ?? "N/A"}</li>
        <li>Rent €/m²: {data.avg_rent_m2 ?? "N/A"}</li>
      </ul>
    </div>
  );
}

export default MunicipalityPanel;
