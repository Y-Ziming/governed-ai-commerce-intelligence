# AI Cost & Usage Observability v0.1

## Objective

Provide request-level visibility into AI usage while keeping Azure billing data as the financial source of truth.

## Request-Level Telemetry

Each programmatic Microsoft Foundry generation records:

* timestamp
* operation type
* model deployment
* prompt version
* contract version
* data classification
* input tokens
* output tokens
* total tokens
* request duration
* response identifier
* generation status

## Financial Source of Truth

Application telemetry is used for operational analysis and cost attribution.

Actual financial cost is reconciled against Azure Cost Management billing and meter data.

Model prices are not hard-coded into the application because actual billing can depend on:

* model
* deployment type
* Azure pricing changes
* subscription agreement
* billing meter

## Cost Governance Principles

1. Record token consumption per request.
2. Track prompt and model versions.
3. Compare output quality against token consumption.
4. Avoid using larger models unless evaluation results justify them.
5. Use Azure Cost Management as the financial source of truth.
6. Review evaluator costs separately from production inference costs.
7. Prefer sampled or release-time semantic evaluation where continuous evaluation provides insufficient additional value.

## Current Status

Request-level token telemetry:
IMPLEMENTED

Azure billing reconciliation:
PLANNED

Automated budget alerting:
PLANNED

Model cost / quality comparison:
PLANNED

