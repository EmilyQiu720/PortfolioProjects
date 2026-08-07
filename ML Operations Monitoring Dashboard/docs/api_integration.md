# API Integration

## Backend

This frontend is designed to connect to:

```text
Production ML Risk Scoring API
```

Expected local backend:

```text
http://127.0.0.1:8000
```

## Environment Variables

Create `.env.local`:

```text
VITE_RISK_API_BASE_URL=http://127.0.0.1:8000
VITE_RISK_API_KEY=dev-local-key
```

## Live Scoring Probe

`src/components/ScoreConsole.tsx` sends a sample request through:

```ts
scoreTransaction(payload)
```

Implemented in:

```text
src/api/riskApi.ts
```

The request maps to:

```text
POST /v1/score
```

with:

```text
x-api-key: dev-local-key
```

## Future Monitoring Endpoints

The dashboard mock data can later be replaced by real endpoints:

| UI Area | Proposed Endpoint |
|---|---|
| KPI cards | `GET /v1/metrics/summary` |
| Volume and latency | `GET /v1/metrics/timeseries` |
| Decision mix | `GET /v1/metrics/decisions` |
| Feature drift | `GET /v1/monitoring/drift` |
| Prediction audit | `GET /v1/predictions?limit=50` |
| Model registry | `GET /v1/model` |

## Failure State

If the backend is not running, the dashboard remains usable with mock monitoring data. The scoring probe shows a readable API error inside the panel.

