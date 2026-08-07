import type { Decision } from "../types";

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatScore(value: number): string {
  return value.toFixed(2);
}

export function decisionLabel(decision: Decision): string {
  if (decision === "manual_review") return "Manual Review";
  return decision.charAt(0).toUpperCase() + decision.slice(1);
}

export function decisionClass(decision: Decision): string {
  return `decision decision-${decision}`;
}
