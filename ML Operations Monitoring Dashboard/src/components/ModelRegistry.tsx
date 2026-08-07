import { GitBranch, ShieldCheck } from "lucide-react";
import type { ModelMetadata } from "../types";

type Props = {
  metadata: ModelMetadata;
};

export function ModelRegistry({ metadata }: Props) {
  return (
    <section className="panel registry-panel" id="registry">
      <div className="panel-heading">
        <div>
          <h2>Model Registry</h2>
          <p>Active model, thresholds, and training metrics</p>
        </div>
        <ShieldCheck size={21} />
      </div>
      <div className="registry-grid">
        <div>
          <span>Active version</span>
          <strong><GitBranch size={16} /> {metadata.modelVersion}</strong>
        </div>
        <div>
          <span>ROC AUC</span>
          <strong>{metadata.rocAuc.toFixed(3)}</strong>
        </div>
        <div>
          <span>Avg precision</span>
          <strong>{metadata.averagePrecision.toFixed(3)}</strong>
        </div>
        <div>
          <span>Brier score</span>
          <strong>{metadata.brierScore.toFixed(3)}</strong>
        </div>
        <div>
          <span>Review threshold</span>
          <strong>{metadata.reviewThreshold.toFixed(2)}</strong>
        </div>
        <div>
          <span>Decline threshold</span>
          <strong>{metadata.declineThreshold.toFixed(2)}</strong>
        </div>
      </div>
    </section>
  );
}
