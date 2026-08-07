import type { DecisionMetric, DriftMetric, Kpi, ModelMetadata, PredictionLog, TimePoint } from "../types";

export const kpis: Kpi[] = [
  { label: "p95 latency", value: "87 ms", delta: "-12 ms vs prior hour", status: "good" },
  { label: "approval rate", value: "72.4%", delta: "+1.8 pts today", status: "good" },
  { label: "manual review", value: "21.8%", delta: "+4.1 pts over baseline", status: "watch" },
  { label: "decline rate", value: "5.8%", delta: "-0.6 pts today", status: "neutral" },
  { label: "drift alerts", value: "2", delta: "velocity and order amount", status: "risk" }
];

export const timeSeries: TimePoint[] = [
  { label: "08:00", requests: 740, latency: 92, reviewRate: 18 },
  { label: "09:00", requests: 980, latency: 86, reviewRate: 19 },
  { label: "10:00", requests: 1210, latency: 84, reviewRate: 21 },
  { label: "11:00", requests: 1180, latency: 89, reviewRate: 24 },
  { label: "12:00", requests: 1360, latency: 87, reviewRate: 22 },
  { label: "13:00", requests: 1510, latency: 93, reviewRate: 25 },
  { label: "14:00", requests: 1440, latency: 88, reviewRate: 23 },
  { label: "15:00", requests: 1620, latency: 87, reviewRate: 22 }
];

export const decisionMetrics: DecisionMetric[] = [
  { decision: "approve", label: "Approve", value: 72.4, count: 8642 },
  { decision: "manual_review", label: "Manual Review", value: 21.8, count: 2603 },
  { decision: "decline", label: "Decline", value: 5.8, count: 693 }
];

export const driftMetrics: DriftMetric[] = [
  { feature: "velocity_score", psi: 0.28, status: "drift", owner: "Risk Features" },
  { feature: "order_amount", psi: 0.18, status: "watch", owner: "Payments" },
  { feature: "ip_risk_score", psi: 0.09, status: "stable", owner: "Trust Signals" },
  { feature: "device_age_days", psi: 0.05, status: "stable", owner: "Device Graph" },
  { feature: "prior_chargebacks_180d", psi: 0.12, status: "watch", owner: "Fraud Ops" }
];

export const predictionLogs: PredictionLog[] = [
  {
    requestId: "REQ-100218",
    modelVersion: "risk-logit-2026-08-05",
    score: 0.84,
    decision: "decline",
    latencyMs: 91,
    topFactors: ["risky IP", "transaction velocity", "prior chargebacks"],
    scoredAt: "15:05:18"
  },
  {
    requestId: "REQ-100407",
    modelVersion: "risk-logit-2026-08-05",
    score: 0.57,
    decision: "manual_review",
    latencyMs: 82,
    topFactors: ["order amount", "new device", "shipping distance"],
    scoredAt: "15:04:42"
  },
  {
    requestId: "REQ-100512",
    modelVersion: "risk-logit-2026-08-05",
    score: 0.12,
    decision: "approve",
    latencyMs: 74,
    topFactors: ["mature account", "low IP risk"],
    scoredAt: "15:03:59"
  },
  {
    requestId: "REQ-100610",
    modelVersion: "risk-logit-2026-08-05",
    score: 0.46,
    decision: "manual_review",
    latencyMs: 95,
    topFactors: ["billing mismatch", "velocity score"],
    scoredAt: "15:03:21"
  }
];

export const modelMetadata: ModelMetadata = {
  modelName: "transaction_risk_logistic_baseline",
  modelVersion: "risk-logit-2026-08-05",
  rocAuc: 0.913,
  averagePrecision: 0.684,
  brierScore: 0.071,
  reviewThreshold: 0.42,
  declineThreshold: 0.78
};
