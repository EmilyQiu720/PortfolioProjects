import type { ScoreResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_RISK_API_BASE_URL ?? "http://127.0.0.1:8000";
const API_KEY = import.meta.env.VITE_RISK_API_KEY ?? "dev-local-key";

export type ScorePayload = {
  request_id: string;
  customer_id: string;
  customer_segment: "consumer" | "small_business" | "enterprise";
  channel: "web" | "mobile" | "partner_api" | "call_center";
  account_age_days: number;
  prior_transactions_30d: number;
  prior_chargebacks_180d: number;
  failed_payment_attempts_24h: number;
  order_amount: number;
  shipping_distance_km: number;
  device_age_days: number;
  email_domain_age_days: number;
  ip_risk_score: number;
  billing_shipping_match: boolean;
  velocity_score: number;
};

export async function scoreTransaction(payload: ScorePayload): Promise<ScoreResponse> {
  const response = await fetch(`${API_BASE_URL}/v1/score`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY
    },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const details = await response.text();
    throw new Error(`Scoring request failed: ${response.status} ${details}`);
  }
  return response.json() as Promise<ScoreResponse>;
}

export async function getHealth(): Promise<{ status: string; model_version: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health request failed: ${response.status}`);
  }
  return response.json() as Promise<{ status: string; model_version: string }>;
}
