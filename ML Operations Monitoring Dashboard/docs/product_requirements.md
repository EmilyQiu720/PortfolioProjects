# Product Requirements

## User Personas

### ML Platform Engineer

Needs to monitor latency, request volume, model version, and API health.

### Risk Operations Lead

Needs to understand approve, manual-review, and decline rates plus recent high-risk decisions.

### Data Scientist

Needs to monitor score distribution, drift, feature shifts, and delayed-label quality signals.

## Core Workflows

1. Check whether the model service is healthy.
2. Confirm traffic and latency are within expected bounds.
3. Investigate why manual review or decline rates changed.
4. Identify drifted features and owning teams.
5. Audit a recent prediction by request ID.
6. Run a sample scoring request against the backend.

## MVP Scope

- Operational dashboard homepage
- KPI cards
- Request/latency trend
- Decision distribution
- Drift table
- Prediction audit table
- Model registry panel
- Live scoring probe
- Responsive layout

## Non-Goals

- Full authentication implementation
- User management
- Model retraining UI
- Human review queue editing
- Alert acknowledgement workflow

These can be added in later portfolio iterations if the project becomes a larger ML platform.

