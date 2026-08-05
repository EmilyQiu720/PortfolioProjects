"""FastAPI application for online and batch risk scoring."""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI

from .batch import score_csv
from .cache import PredictionCache
from .config import settings
from .features import stable_hash
from .model import ModelArtifact
from .schemas import BatchScoreRequest, BatchScoreResponse, HealthResponse, RiskInput, RiskResponse
from .scoring import score_record
from .security import require_api_key
from .storage import PredictionStore


app = FastAPI(title=settings.app_name, version="1.0.0")
model = ModelArtifact.from_path(settings.model_registry_path)
store = PredictionStore(settings.database_path)
cache = PredictionCache()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        model_version=model.model_version,
        environment=settings.environment,
    )


@app.post("/v1/score", response_model=RiskResponse, dependencies=[Depends(require_api_key)])
def score(input_record: RiskInput) -> RiskResponse:
    payload = input_record.model_dump(mode="json")
    cache_key = f"{payload['request_id']}:{model.model_version}"
    cached = cache.get(cache_key)
    if cached is not None:
        return RiskResponse(**cached)
    prediction = score_record(payload, model)
    store.insert_prediction(prediction, stable_hash(input_record.customer_id))
    response = RiskResponse(**prediction)
    cache.set(cache_key, response.model_dump(mode="json"))
    return response


@app.post("/v1/batch-score", response_model=BatchScoreResponse, dependencies=[Depends(require_api_key)])
def batch_score(request: BatchScoreRequest) -> BatchScoreResponse:
    rows_scored = score_csv(Path(request.input_path), Path(request.output_path), model)
    return BatchScoreResponse(rows_scored=rows_scored, output_path=request.output_path)


@app.get("/v1/prediction-summary", dependencies=[Depends(require_api_key)])
def prediction_summary() -> dict[str, object]:
    return store.summary()

