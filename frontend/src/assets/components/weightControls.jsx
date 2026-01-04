export default function WeightControls({ weights, onChange }) {
  return (
    <div className="p-4 grid grid-cols-2 gap-4">
      {Object.keys(weights).map(key => (
        <div key={key}>
          <label className="capitalize">{key}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={weights[key]}
            onChange={e => onChange(key, parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
      ))}
    </div>
  );
}
