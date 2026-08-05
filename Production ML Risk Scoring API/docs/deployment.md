# Deployment

## Local Docker

```powershell
docker compose up --build
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `APP_ENV` | local, docker, staging, production |
| `API_KEY` | API key required by protected endpoints |
| `DATABASE_PATH` | SQLite prediction log path for local demo |
| `MODEL_REGISTRY_PATH` | model registry artifact path |
| `REFERENCE_FEATURES_PATH` | baseline data for drift monitoring |
| `ENABLE_CACHE` | cache toggle |
| `REDIS_URL` | Redis URL for production extension |
| `REQUEST_TIMEOUT_SECONDS` | request timeout target |

## Production Notes

For production, replace local SQLite with PostgreSQL or a managed warehouse table. Keep the same prediction-log columns so downstream monitoring and dashboards remain stable.

Recommended deployment stack:

- Docker image built in CI
- API service behind a gateway or load balancer
- secrets stored in a secret manager
- PostgreSQL prediction log
- Redis cache for idempotent repeat requests
- OpenTelemetry traces
- Prometheus/Grafana or cloud-native metrics
- separate batch worker for large CSV jobs

## Release Checklist

- Validate request schema compatibility.
- Run unit tests.
- Run batch scoring smoke test.
- Confirm model registry active version.
- Confirm thresholds are approved.
- Confirm prediction logging is working.
- Confirm rollback image/model version is available.

