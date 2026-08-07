import type { DecisionMetric } from "../types";
import { decisionClass, formatPercent } from "../utils/format";

type Props = {
  data: DecisionMetric[];
};

export function DecisionMix({ data }: Props) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Decision Mix</h2>
          <p>Routing distribution from the active model thresholds</p>
        </div>
      </div>
      <div className="bar-list">
        {data.map((item) => (
          <div className="bar-row" key={item.decision}>
            <div className="bar-meta">
              <span className={decisionClass(item.decision)}>{item.label}</span>
              <span>{item.count.toLocaleString()} requests</span>
            </div>
            <div className="bar-track">
              <div className={`bar-fill fill-${item.decision}`} style={{ width: `${item.value}%` }} />
            </div>
            <strong>{formatPercent(item.value)}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
