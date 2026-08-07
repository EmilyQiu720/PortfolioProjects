import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import type { Kpi } from "../types";

type Props = {
  item: Kpi;
};

export function KpiCard({ item }: Props) {
  const Icon = item.status === "good" ? ArrowUpRight : item.status === "risk" ? ArrowDownRight : Minus;
  return (
    <section className={`kpi-card kpi-${item.status}`}>
      <div className="kpi-label">{item.label}</div>
      <div className="kpi-value">{item.value}</div>
      <div className="kpi-delta">
        <Icon size={15} strokeWidth={2.2} />
        <span>{item.delta}</span>
      </div>
    </section>
  );
}
