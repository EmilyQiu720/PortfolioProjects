import type { TimePoint } from "../types";

type Props = {
  data: TimePoint[];
};

function points(values: number[], width: number, height: number, padding: number): string {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  return values
    .map((value, index) => {
      const x = padding + (index / Math.max(values.length - 1, 1)) * (width - padding * 2);
      const y = height - padding - ((value - min) / range) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(" ");
}

export function LineChart({ data }: Props) {
  const width = 520;
  const height = 230;
  const requestPoints = points(data.map((row) => row.requests), width, height, 28);
  const latencyPoints = points(data.map((row) => row.latency), width, height, 28);

  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <h2>Scoring Volume and Latency</h2>
          <p>Hourly production traffic and serving performance</p>
        </div>
        <div className="legend">
          <span><i className="legend-primary" /> Requests</span>
          <span><i className="legend-secondary" /> p95 latency</span>
        </div>
      </div>
      <svg className="line-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Scoring volume and latency chart">
        <line x1="28" y1="196" x2="492" y2="196" className="axis" />
        <polyline points={requestPoints} className="line-primary" />
        <polyline points={latencyPoints} className="line-secondary" />
        {data.map((row, index) => {
          const x = 28 + (index / Math.max(data.length - 1, 1)) * (width - 56);
          return (
            <text key={row.label} x={x} y="220" textAnchor="middle" className="chart-label">
              {index % 2 === 0 ? row.label : ""}
            </text>
          );
        })}
      </svg>
    </section>
  );
}
