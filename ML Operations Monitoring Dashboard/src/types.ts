export type Decision = "approve" | "manual_review" | "decline";

export type Kpi = {
  label: string;
  value: string;
  delta: string;
  status: "good" | "watch" | "risk" | "neutral";
};

export type TimePoint = {
  label: string;
  requests: number;
  latency: number;
  reviewRate: number;
};

export type DecisionMetric = {
  decision: Decision;
  label: string;
  value: number;
  count: number;
};

export type DriftMetric = {
  feature: string;
  psi: number;
  status: "stable" | "watch" | "drift";
  owner: string;
};

export type PredictionLog = {
  requestId: string;
  modelVersion: string;
  score: number;
  decision: Decision;
  latencyMs: number;
  topFactors: string[];
  scoredAt: string;
};

export type ModelMetadata = {
  modelName: string;
  modelVersion: string;
  rocAuc: number;
  averagePrecision: number;
  brierScore: number;
  reviewThreshold: number;
  declineThreshold: number;
};

export type ScoreResponse = {
  request_id: string;
  model_name: string;
  model_version: string;
  risk_score: number;
  risk_decision: Decision;
  top_factors: string[];
  scored_at: string;
};
