import type { PredictionLog } from "../types";
import { decisionClass, decisionLabel, formatScore } from "../utils/format";

type Props = {
  rows: PredictionLog[];
};

export function PredictionTable({ rows }: Props) {
  return (
    <section className="panel wide-panel" id="predictions">
      <div className="panel-heading">
        <div>
          <h2>Prediction Log Audit</h2>
          <p>Recent scores with model version, decision, latency, and explanation factors</p>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Request</th>
            <th>Score</th>
            <th>Decision</th>
            <th>Latency</th>
            <th>Top Factors</th>
            <th>Scored</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.requestId}>
              <td>{row.requestId}</td>
              <td>{formatScore(row.score)}</td>
              <td><span className={decisionClass(row.decision)}>{decisionLabel(row.decision)}</span></td>
              <td>{row.latencyMs} ms</td>
              <td>{row.topFactors.join(", ")}</td>
              <td>{row.scoredAt}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
