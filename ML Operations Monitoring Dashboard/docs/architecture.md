# Architecture

## Frontend Structure

```text
App
  Topbar
  Sidebar
  KPI Cards
  LineChart
  DecisionMix
  ModelRegistry
  DriftTable
  PredictionTable
  ScoreConsole
```

## Data Sources

The current dashboard uses two data modes:

- Mock monitoring data from `src/data/mockData.ts`
- Live scoring API calls from `src/api/riskApi.ts`

The mock data makes the portfolio project reviewable without requiring the backend service to be running. The scoring probe demonstrates how the frontend integrates with the backend when it is available.

## Component Responsibilities

| Component | Responsibility |
|---|---|
| `KpiCard` | Render latency, approval, manual review, decline, and drift KPIs |
| `LineChart` | Render request volume and latency trends |
| `DecisionMix` | Show approve/manual-review/decline distribution |
| `DriftTable` | Show feature PSI and drift status |
| `PredictionTable` | Show recent prediction audit records |
| `ModelRegistry` | Show active model version, thresholds, and training metrics |
| `ScoreConsole` | Send sample scoring requests to the FastAPI backend |

## Design Principles

- Dense but readable operational dashboard layout
- Stable card and chart dimensions to avoid layout shift
- Clear risk states using text plus color
- No landing-page hero
- No decorative gradients or marketing sections
- Frontend focused on repeated monitoring workflows

## Production Extensions

Recommended production additions:

- TanStack Query or SWR for request caching and retries
- Role-based access control
- WebSocket/SSE live updates
- Alert acknowledgement workflow
- Request ID search backed by API
- Real monitoring endpoints for latency, drift, and prediction logs
- E2E tests with Playwright

