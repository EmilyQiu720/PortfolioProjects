import { useState } from "react";
import { PlayCircle } from "lucide-react";
import { scoreTransaction, type ScorePayload } from "../api/riskApi";
import type { ScoreResponse } from "../types";
import { decisionClass, decisionLabel } from "../utils/format";

const samplePayload: ScorePayload = {
  request_id: "REQ-DEMO-2001",
  customer_id: "CUST-87420",
  customer_segment: "consumer",
  channel: "mobile",
  account_age_days: 12,
  prior_transactions_30d: 27,
  prior_chargebacks_180d: 2,
  failed_payment_attempts_24h: 4,
  order_amount: 2800.5,
  shipping_distance_km: 1200,
  device_age_days: 3,
  email_domain_age_days: 15,
  ip_risk_score: 0.82,
  billing_shipping_match: false,
  velocity_score: 0.91
};

export function ScoreConsole() {
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function runScore() {
    setLoading(true);
    setError(null);
    try {
      const response = await scoreTransaction({
        ...samplePayload,
        request_id: `REQ-DEMO-${Math.floor(Math.random() * 9000 + 1000)}`
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown scoring error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel score-console">
      <div className="panel-heading">
        <div>
          <h2>Live Scoring Probe</h2>
          <p>Calls the FastAPI backend when it is running locally</p>
        </div>
        <button onClick={runScore} type="button" disabled={loading} title="Run sample score">
          <PlayCircle size={17} />
          {loading ? "Scoring" : "Score sample"}
        </button>
      </div>
      <pre>{JSON.stringify(samplePayload, null, 2)}</pre>
      {result && (
        <div className="score-result">
          <span className={decisionClass(result.risk_decision)}>{decisionLabel(result.risk_decision)}</span>
          <strong>{result.risk_score.toFixed(3)}</strong>
          <small>{result.top_factors.join(", ")}</small>
        </div>
      )}
      {error && <div className="api-error">{error}</div>}
    </section>
  );
}
