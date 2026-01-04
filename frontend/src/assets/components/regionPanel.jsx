export default function RegionPanel({ region }) {
  if (!region) return <div>Select a region.</div>;

  return (
    <div className="p-4 border rounded bg-gray-100">
      <h2 className="text-xl font-bold capitalize">{region.region}</h2>
      <p>Salary: {region.salary}</p>
      <p>Housing: {region.housing}</p>
      <p>Pollution: {region.pollution}</p>
      <p>Health: {region.health}</p>
    </div>
  );
}
