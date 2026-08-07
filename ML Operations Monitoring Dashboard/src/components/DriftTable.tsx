import { AlertTriangle, CheckCircle2, CircleDashed } from "lucide-react";
import type { DriftMetric } from "../types";

type Props = {
  rows: DriftMetric[];
};

export function DriftTable({ rows }: Props) {
  return (
    <section className="panel" id="drift">
      <div className="panel-heading">
        <div>
          <h2>Feature Drift Monitor</h2>
          <p>Population Stability Index by scoring feature</p>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Feature</th>
            <th>PSI</th>
            <th>Status</th>
            <th>Owner</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const Icon = row.status === "stable" ? CheckCircle2 : row.status === "watch" ? CircleDashed : AlertTriangle;
            return (
              <tr key={row.feature}>
                <td>{row.feature}</td>
                <td>{row.psi.toFixed(2)}</td>
                <td>
                  <span className={`status status-${row.status}`}>
                    <Icon size={14} />
                    {row.status}
                  </span>
                </td>
                <td>{row.owner}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
