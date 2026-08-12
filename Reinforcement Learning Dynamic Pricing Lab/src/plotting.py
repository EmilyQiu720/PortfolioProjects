"""SVG plotting and portfolio asset generation."""

from __future__ import annotations

from pathlib import Path

from .config import ACTION_NAMES
from .evaluation import PolicySummary
from .environment import State
from .q_learning import QTable


def plot_training_curve(path: Path, rewards: list[float]) -> None:
    """Save a smoothed reward curve as dependency-free SVG."""

    path.parent.mkdir(parents=True, exist_ok=True)
    window = 30
    smoothed = [
        sum(rewards[max(0, index - window + 1) : index + 1]) / len(rewards[max(0, index - window + 1) : index + 1])
        for index in range(len(rewards))
    ]
    raw_points = _line_points(rewards, 80, 80, 900, 360)
    smooth_points = _line_points(smoothed, 80, 80, 900, 360)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="520" viewBox="0 0 1060 520">
  <rect width="1060" height="520" fill="#ffffff"/>
  <text x="80" y="44" font-family="Segoe UI, Arial, sans-serif" font-size="26" font-weight="700" fill="#1f2937">Q-Learning Training Curve</text>
  <line x1="80" y1="440" x2="980" y2="440" stroke="#d7dde6"/>
  <line x1="80" y1="80" x2="80" y2="440" stroke="#d7dde6"/>
  <polyline points="{raw_points}" fill="none" stroke="#c7c1f4" stroke-width="1.2" opacity="0.55"/>
  <polyline points="{smooth_points}" fill="none" stroke="#8074a8" stroke-width="3"/>
  <rect x="740" y="74" width="14" height="14" fill="#c7c1f4" opacity="0.65"/><text x="764" y="88" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#64748b">episode reward</text>
  <rect x="740" y="102" width="14" height="14" fill="#8074a8"/><text x="764" y="116" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#64748b">30-episode moving average</text>
  <text x="490" y="492" font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#64748b">Episode</text>
  <text x="16" y="270" transform="rotate(-90 16 270)" font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#64748b">Reward</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def plot_policy_heatmap(path: Path, q_table: QTable) -> None:
    """Save a heatmap of greedy actions by inventory and price buckets."""

    path.parent.mkdir(parents=True, exist_ok=True)
    colors = ["#c05a84", "#c7c1f4", "#e5e7eb", "#8bcac1", "#0f766e"]
    cells = []
    for inventory_bucket in range(6):
        for price_bucket in range(6):
            state: State = (5 - inventory_bucket, price_bucket, 1, 1, 3)
            values = q_table.get(state, [0.0] * len(ACTION_NAMES))
            action = max(range(len(values)), key=lambda index: values[index])
            x = 150 + price_bucket * 92
            y = 88 + inventory_bucket * 58
            cells.append(
                f'<rect x="{x}" y="{y}" width="86" height="52" rx="5" fill="{colors[action]}"/>'
                f'<text x="{x + 43}" y="{y + 32}" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="12" fill="#111827">{ACTION_NAMES[action]}</text>'
            )
    legend = []
    for index, name in enumerate(ACTION_NAMES):
        y = 92 + index * 38
        legend.append(
            f'<rect x="760" y="{y}" width="18" height="18" fill="{colors[index]}"/>'
            f'<text x="790" y="{y + 15}" font-family="Segoe UI, Arial, sans-serif" font-size="14" fill="#475569">{name}</text>'
        )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="980" height="500" viewBox="0 0 980 500">
  <rect width="980" height="500" fill="#ffffff"/>
  <text x="80" y="44" font-family="Segoe UI, Arial, sans-serif" font-size="26" font-weight="700" fill="#1f2937">Learned Pricing Policy Heatmap</text>
  <text x="314" y="474" font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#64748b">Price bucket</text>
  <text x="22" y="262" transform="rotate(-90 22 262)" font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#64748b">Inventory bucket</text>
  {''.join(cells)}
  {''.join(_axis_labels())}
  {''.join(legend)}
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def write_portfolio_preview(path: Path, summaries: list[PolicySummary]) -> None:
    """Create a lightweight SVG preview for GitHub Pages."""

    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(summaries, key=lambda item: item.mean_profit, reverse=True)
    max_profit = max(summary.mean_profit for summary in ordered)
    rows = []
    for index, summary in enumerate(ordered[:5]):
        y = 318 + index * 54
        width = max(80, int(430 * summary.mean_profit / max_profit))
        color = "#0f766e" if summary.policy == "q_learning" else "#8074a8" if index < 3 else "#c05a84"
        rows.append(
            f'<text x="1040" y="{y + 18}" font-size="18" fill="#334155">{summary.policy}</text>'
            f'<rect x="1220" y="{y}" width="{width}" height="26" rx="4" fill="{color}"/>'
            f'<text x="{1230 + width}" y="{y + 19}" font-size="16" fill="#334155">${summary.mean_profit:,.0f}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <rect width="1600" height="900" fill="#f3f6fa"/>
  <rect x="0" y="0" width="1600" height="112" fill="#111827"/>
  <text x="44" y="50" font-family="Segoe UI, Arial, sans-serif" font-size="35" font-weight="700" fill="#ffffff">Reinforcement Learning Dynamic Pricing Lab</text>
  <text x="44" y="82" font-family="Segoe UI, Arial, sans-serif" font-size="18" fill="#cbd5e1">Custom MDP simulator, Q-learning policy, baseline comparison, and risk-aware reward evaluation</text>
  <g font-family="Segoe UI, Arial, sans-serif">
    <rect x="44" y="154" width="430" height="612" rx="8" fill="#ffffff" stroke="#d7e0ea"/>
    <text x="76" y="202" font-size="26" font-weight="700" fill="#1f2937">MDP Design</text>
    <text x="76" y="252" font-size="18" font-weight="700" fill="#475569">State</text>
    <text x="76" y="284" font-size="16" fill="#64748b">inventory bucket, price bucket, competitor</text>
    <text x="76" y="308" font-size="16" fill="#64748b">position, seasonality bucket</text>
    <text x="76" y="360" font-size="18" font-weight="700" fill="#475569">Actions</text>
    <text x="76" y="392" font-size="16" fill="#64748b">large discount, small discount, hold,</text>
    <text x="76" y="416" font-size="16" fill="#64748b">small increase, large increase</text>
    <text x="76" y="468" font-size="18" font-weight="700" fill="#475569">Reward</text>
    <rect x="76" y="494" width="340" height="74" rx="6" fill="#111827"/>
    <text x="98" y="526" font-family="Consolas, monospace" font-size="15" fill="#d1d5db">profit - stockout risk</text>
    <text x="98" y="550" font-family="Consolas, monospace" font-size="15" fill="#d1d5db">- price volatility penalty</text>
    <text x="76" y="626" font-size="18" font-weight="700" fill="#475569">Evaluation</text>
    <text x="76" y="658" font-size="16" fill="#64748b">multi-seed rollouts, confidence intervals,</text>
    <text x="76" y="682" font-size="16" fill="#64748b">profit, revenue, stockout, volatility</text>
    <rect x="532" y="154" width="444" height="612" rx="8" fill="#ffffff" stroke="#d7e0ea"/>
    <text x="564" y="202" font-size="26" font-weight="700" fill="#1f2937">Training Loop</text>
    <circle cx="754" cy="304" r="78" fill="#e7f6f3" stroke="#b7e1d9"/>
    <text x="710" y="300" font-size="17" font-weight="700" fill="#0f766e">Observe</text>
    <text x="705" y="324" font-size="15" fill="#0f766e">state</text>
    <circle cx="754" cy="500" r="78" fill="#edf2ff" stroke="#c7d2fe"/>
    <text x="716" y="496" font-size="17" font-weight="700" fill="#4f46e5">Choose</text>
    <text x="712" y="520" font-size="15" fill="#4f46e5">price action</text>
    <circle cx="754" cy="696" r="78" fill="#fff4d8" stroke="#f1d58d"/>
    <text x="722" y="692" font-size="17" font-weight="700" fill="#8a5a10">Update</text>
    <text x="699" y="716" font-size="15" fill="#8a5a10">Q-values</text>
    <line x1="754" y1="382" x2="754" y2="422" stroke="#94a3b8" stroke-width="4"/>
    <polygon points="754,440 742,420 766,420" fill="#94a3b8"/>
    <line x1="754" y1="578" x2="754" y2="618" stroke="#94a3b8" stroke-width="4"/>
    <polygon points="754,636 742,616 766,616" fill="#94a3b8"/>
    <rect x="1028" y="154" width="528" height="612" rx="8" fill="#ffffff" stroke="#d7e0ea"/>
    <text x="1060" y="202" font-size="26" font-weight="700" fill="#1f2937">Policy Comparison</text>
    <text x="1060" y="246" font-size="16" fill="#64748b">Mean profit across repeated evaluation episodes</text>
    {''.join(rows)}
    <rect x="44" y="808" width="1512" height="54" rx="8" fill="#0f172a"/>
    <text x="74" y="842" font-size="16" fill="#cbd5e1">Senior signal: reward shaping, controlled simulation, baseline discipline, reproducible training, multi-metric evaluation, and ablation-ready design</text>
  </g>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def _line_points(values: list[float], x: int, y: int, width: int, height: int) -> str:
    if not values:
        return ""
    low = min(values)
    high = max(values)
    span = high - low if high != low else 1.0
    points = []
    for index, value in enumerate(values):
        px = x + (index / max(1, len(values) - 1)) * width
        py = y + height - ((value - low) / span) * height
        points.append(f"{px:.2f},{py:.2f}")
    return " ".join(points)


def _axis_labels() -> list[str]:
    labels = []
    for index in range(6):
        labels.append(f'<text x="{193 + index * 92}" y="454" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#64748b">{index}</text>')
        labels.append(f'<text x="126" y="{121 + index * 58}" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="13" fill="#64748b">{5 - index}</text>')
    return labels
