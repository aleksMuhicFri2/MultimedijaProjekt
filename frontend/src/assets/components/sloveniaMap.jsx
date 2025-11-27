export default function SloveniaMap({ onSelect }) {
  return (
    <div className="w-full">
      <svg viewBox="0 0 800 400" className="max-w-xl mx-auto cursor-pointer">
        <path
          id="gorenjska"
          d="M10,80 L150,60 L200,120 L150,160 Z"
          onClick={() => onSelect("gorenjska")}
          className="fill-gray-300 hover:fill-blue-300 stroke-black"
        />
        <path
          id="primorska"
          d="M150,160 L200,120 L300,150 L250,220 Z"
          onClick={() => onSelect("primorska")}
          className="fill-gray-300 hover:fill-blue-300 stroke-black"
        />
        <path
          id="stajerska"
          d="M300,150 L400,100 L450,180 L350,230 Z"
          onClick={() => onSelect("stajerska")}
          className="fill-gray-300 hover:fill-blue-300 stroke-black"
        />
      </svg>
    </div>
  );
}