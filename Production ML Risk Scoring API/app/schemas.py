"""Pydantic schemas for API input and output contracts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class Channel(str, Enum):
    web = "web"
    mobile = "mobile"
    partner_api = "partner_api"
    call_center = "call_center"


class CustomerSegment(str, Enum):
    consumer = "consumer"
    small_business = "small_business"
    enterprise = "enterprise"


class RiskInput(BaseModel):
    request_id: Annotated[str, Field(min_length=8, max_length=80)]
    customer_id: Annotated[str, Field(min_length=4, max_length=80)]
    customer_segment: CustomerSegment
    channel: Channel
    account_age_days: Annotated[int, Field(ge=0, le=7300)]
    prior_transactions_30d: Annotated[int, Field(ge=0, le=500)]
    prior_chargebacks_180d: Annotated[int, Field(ge=0, le=50)]
    failed_payment_attempts_24h: Annotated[int, Field(ge=0, le=50)]
    order_amount: Annotated[float, Field(gt=0, le=50000)]
    shipping_distance_km: Annotated[float, Field(ge=0, le=20000)]
    device_age_days: Annotated[int, Field(ge=0, le=7300)]
    email_domain_age_days: Annotated[int, Field(ge=0, le=7300)]
    ip_risk_score: Annotated[float, Field(ge=0, le=1)]
    billing_shipping_match: bool
    velocity_score: Annotated[float, Field(ge=0, le=1)]
    submitted_at: datetime | None = None

    @field_validator("customer_id", "request_id")
    @classmethod
    def strip_ids(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("identifier cannot be blank")
        return cleaned


class RiskDecision(str, Enum):
    approve = "approve"
    manual_review = "manual_review"
    decline = "decline"


class RiskResponse(BaseModel):
    request_id: str
    model_name: str
    model_version: str
    risk_score: float
    risk_decision: RiskDecision
    decision_thresholds: dict[str, float]
    top_factors: list[str]
    scored_at: datetime


class BatchScoreRequest(BaseModel):
    input_path: str
    output_path: str


class BatchScoreResponse(BaseModel):
    rows_scored: int
    output_path: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    model_version: str
    environment: str

