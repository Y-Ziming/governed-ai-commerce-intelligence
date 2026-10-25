# Governed AI Commerce Intelligence

An end-to-end Data & AI transformation case study that converts a fragmented manual e-commerce reporting workflow into a governed analytics and AI decision-support platform.

The project was developed around a real small-business use case in Germany. Real company data remains private. This public repository contains only synthetic or anonymized examples.

## Business Context

The original workflow relied heavily on manually downloaded marketplace order data and spreadsheet-based reporting.

The business needed clearer answers to questions such as:

* Which products are selling best?
* Which regions generate the strongest demand?
* How is performance changing month over month?
* Which data-quality issues could affect decisions?
* How can AI support management interpretation without becoming the source of truth for business KPIs?

The goal was not to add an LLM on top of raw spreadsheets.

The goal was to redesign the workflow from the data layer upward.

## Transformation Approach

The project evolved through five layers:

1. Business discovery and data profiling
2. Canonical data modelling and data-quality controls
3. Deterministic analytics and management dashboard
4. Governed AI decision support with Microsoft Foundry
5. Secure Azure deployment with identity-based access and observability

The resulting architecture deliberately separates deterministic business metrics from probabilistic AI reasoning.

> The LLM never owns the source of truth for business KPIs.

## Implemented Solution

### Data Foundation

Raw operational spreadsheets are transformed into trusted canonical entities for:

* orders
* order lines
* products
* shipments
* quarantined data-quality events

Important identifiers are handled as strings to avoid numeric precision loss.

Direct customer PII is excluded from the analytics and AI layers.

### Deterministic Analytics

Trusted analytics are calculated before any AI interaction.

Implemented analytical views include:

* monthly sales overview
* product performance
* month-over-month comparison
* regional performance
* shipment coverage
* geography mapping coverage
* data-quality indicators

A local Streamlit dashboard was developed for management exploration of product and regional performance.

### Governed AI Management Brief

Microsoft Foundry and GPT-5-mini are used to interpret trusted analytical context and generate a structured management brief.

The AI is allowed to:

* summarize observed performance
* prioritize issues for review
* identify supported patterns
* recommend further investigation

The AI is not allowed to:

* recalculate official KPIs
* invent unavailable metrics
* infer unsupported causal relationships
* expose direct PII
* make autonomous commercial decisions

All AI outputs require human review.

## Defense-in-Depth AI Governance

The project uses multiple independent controls.

### Structured Outputs

A Pydantic schema is supplied through the Microsoft Foundry Responses API.

This constrains:

* required fields
* allowed categories
* confidence values
* recommendation types
* report status
* human-review status

### Deterministic Validation

A Python governance validator checks:

* contract version consistency
* required output structure
* valid evidence references
* allowed categories and action types
* human-review requirements
* evidence-reference consistency

Invalid outputs are blocked.

### Semantic Evaluation

Microsoft Foundry evaluations were used for:

* Groundedness
* Relevance

A custom evaluator was also created for:

* evidence sufficiency
* unsupported associations

A small governance regression suite demonstrated that built-in semantic evaluation and domain-specific governance controls detect different classes of failure.

This produced an important design conclusion:

> Evidence validity, evidence sufficiency, and semantic grounding are different controls.

## Azure Deployment

The governed AI pipeline has been containerized and deployed as an Azure Container Apps Job.

The deployed flow is:

```text
Private aggregated analytics context
        ↓
Azure Blob Storage
        ↓
Azure Container Apps Job
        ↓
Managed Identity
        ↓
Microsoft Foundry / GPT-5-mini
        ↓
Structured Output
        ↓
Deterministic Governance Validation
        ↓
Azure Blob Storage
```

The cloud deployment has been successfully executed with real aggregated business context.

## Security and Privacy

The project follows a deliberately small but practical security baseline:

* no real company data in the public repository
* no direct customer PII sent to the AI layer
* cloud-context boundary validation before model invocation
* no API keys embedded in application code
* no ACR passwords embedded in deployment configuration
* Microsoft Entra ID and Managed Identity for Azure service access
* RBAC scoped to required resources
* anonymous Blob access disabled
* private business outputs stored outside the public repository
* human review required before AI output is treated as decision support

For the current portfolio scope, advanced network isolation such as Private Endpoints and VNet integration is documented as future enterprise hardening rather than implemented infrastructure.

## Observability and Cost Governance

Each programmatic AI generation records:

* model deployment
* prompt version
* contract version
* input tokens
* output tokens
* total tokens
* execution duration
* generation status

Azure Log Analytics captures Container Apps Job execution logs.

Azure Cost Management is treated as the financial source of truth, and a monthly Azure budget alert is configured for the project.

## Key Architecture Decisions

Several technologies were deliberately not added merely to increase architectural complexity.

### No RAG

The current use case operates on structured, precomputed analytical context. Retrieval over an external knowledge corpus is not required.

### No Agent

The system generates decision support but does not autonomously execute business actions.

### No Azure SQL

The current analytical workload does not justify an additional transactional or serving database.

### No LLM-Based KPI Calculation

Business metrics are deterministic and calculated before the model is invoked.

### Human-in-the-Loop by Design

AI output remains a draft requiring human review.

## Repository Structure

```text
architecture/
    target architecture and architecture decisions

data/
    synthetic public examples only

docs/
    AI contract, evaluation, governance and experiment documentation

prompts/
    versioned management-brief system prompts

src/ai/
    context validation, structured-output schema,
    Foundry generation and governance pipeline

tests/
    synthetic validation and evaluation evidence

screenshots/
    sanitized portfolio evidence

Dockerfile
requirements.txt
README.md
```

## Project Status

Implemented:

* business workflow analysis
* canonical data model
* data-quality controls
* deterministic analytics
* regional analytics
* management dashboard
* AI context boundary
* Microsoft Foundry integration
* structured AI outputs
* deterministic governance validation
* built-in semantic evaluation
* custom governance evaluation
* governance regression testing
* token observability
* Docker containerization
* Azure Container Registry
* Azure Blob Storage integration
* Azure Container Apps Job
* Managed Identity and RBAC
* Log Analytics
* Azure budget control
* private aggregated cloud execution

Future / enterprise hardening:

* private endpoints
* VNet-based network isolation
* automated CI/CD
* infrastructure as code
* expanded production evaluation datasets

## Core Design Principle

The project treats AI as a governed reasoning layer on top of trusted deterministic analytics, not as a replacement for the data foundation.

The architecture therefore follows:

**Trusted data → deterministic metrics → governed AI reasoning → validation → human review.**
