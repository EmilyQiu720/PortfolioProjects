# Architecture

## Service Flow

```text
Client
  -> FastAPI route
  -> API key guard
  -> Pydantic request validation
  -> feature transformation
  -> model artifact runtime
  -> decision policy
  -> prediction log
  -> response contract
```

## Runtime Components

| Component | File | Responsibility |
|---|---|---|
| API routes | `app/main.py` | Versioned HTTP endpoints |
| Schemas | `app/schemas.py` | Request and response contracts |
| Feature layer | `app/features.py` | Numeric/categorical validation and model-ready transforms |
| Model runtime | `app/model.py` | Load model artifact, compute probability, explain top factors |
| Scoring policy | `app/scoring.py` | Convert probability into approve/review/decline decisions |
| Prediction store | `app/storage.py` | Persist request-level score logs |
| Drift monitoring | `app/drift.py` | Population Stability Index |
| Batch scoring | `app/batch.py` | CSV scoring workflow |
| Security | `app/security.py` | API key authentication |

## Design Choices

- The model artifact is stored outside code so model versions and thresholds can be audited.
- The feature transformation layer is shared across online and batch paths to avoid training/serving skew.
- Request schemas validate feature ranges before inference.
- Customer identifiers are hashed before persistence.
- The local store uses SQLite for portability; the schema maps directly to PostgreSQL.
- API responses include model version and thresholds so downstream systems can trace decisions.

## Production Extensions

In a real deployment, this service would usually add:

- PostgreSQL or warehouse-backed prediction logging
- Redis or managed cache for repeated idempotent scores
- OpenTelemetry traces and metrics
- Rate limiting and tenant-level authorization
- Feature store integration
- Model registry integration such as MLflow, SageMaker Model Registry, or Vertex AI Model Registry
- Canary deployment and shadow scoring
- Async batch queue using Celery, Sidekiq-style workers, or cloud-native jobs

