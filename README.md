# Governed AI Commerce Intelligence

**An end-to-end Data & AI transformation case study built around a real small-business e-commerce workflow in Germany.**

The project transforms a fragmented, spreadsheet-heavy reporting process into a governed analytics and AI decision-support platform using Python, Microsoft Foundry and Azure.

> **Core design principle:** trusted data → deterministic metrics → governed AI reasoning → validation → human review.

Real company data remains private. This public repository contains only synthetic or anonymized examples.

---

## Architecture at a Glance

<img width="1536" height="1024" alt="Target architecture" src="https://github.com/user-attachments/assets/6f08f36b-b196-41e0-b1e9-eb4cfa952c31" />


## Business Problem

The original workflow relied heavily on manually downloaded marketplace data and spreadsheet-based reporting.

Management needed clearer answers to questions such as:

* Which products are selling best?
* Which regions generate the strongest demand?
* How is performance changing month over month?
* Which data-quality issues could affect decisions?
* Where can AI add value without becoming the source of truth for business metrics?

The project therefore started with business discovery and workflow analysis rather than with an LLM.

---

## What I Built

### 1. Data Foundation

Operational spreadsheets are transformed into trusted canonical entities for orders, order lines, products, shipments and quarantined data-quality events.

Important identifiers are handled as strings to avoid numeric precision loss.

Direct customer PII is excluded from the analytics and AI layers.

### 2. Deterministic Analytics

Business KPIs are calculated before the model is invoked.

Implemented analytical views include:

* monthly sales performance
* product performance
* month-over-month comparison
* regional performance
* shipment coverage
* geographic mapping coverage
* data-quality indicators

A Streamlit management dashboard was developed for product and regional analysis.

### 3. Governed AI Management Brief

Microsoft Foundry and GPT-5-mini interpret trusted aggregated metrics and generate a structured management brief.

The LLM may summarize, interpret and recommend investigation.

It does **not** own or recalculate official business KPIs.

### 4. AI Governance

The AI layer uses defense-in-depth controls:

* Pydantic-based Structured Outputs
* evidence references
* deterministic validation
* Microsoft Foundry Groundedness and Relevance evaluation
* custom evidence-sufficiency evaluation
* governance regression testing
* human-in-the-loop review
* cloud-context boundary validation

A key project finding was:

> **Evidence validity, evidence sufficiency and semantic grounding are different controls.**

<img width="1168" height="404" alt="02_foundry_evaluations_overview" src="https://github.com/user-attachments/assets/61b74d4a-821d-4c07-adaa-d1be2d92aca6" />


### 5. Azure Deployment

The governed AI pipeline was containerized and deployed as an Azure Container Apps Job.

The deployed private-data flow is:

```text
Private aggregated analytics context
        ↓
Azure Blob Storage
        ↓
Azure Container Apps Job
        ↓
Managed Identity
        ↓
Microsoft Foundry
        ↓
Structured Output
        ↓
Governance Validation
        ↓
Azure Blob Storage
```

No API keys or ACR passwords are embedded in the application.

<img width="948" height="588" alt="04_azure_pipeline_log_analytics" src="https://github.com/user-attachments/assets/e269a08b-01ce-4d89-b7e9-89e39a8913ab" />


The cloud pipeline has been successfully executed using real aggregated business context while keeping raw operational data and direct PII outside the public repository.

<img width="984" height="447" alt="05_blob_ai_output_overview" src="https://github.com/user-attachments/assets/bc2ff7a0-ad49-4fba-95f5-685cbc885fd5" />

---

## Security and Privacy

The portfolio uses a deliberately small but practical security baseline:

* real company data never enters the public GitHub repository
* direct customer PII is excluded from the AI context
* private data is checked before being sent to Foundry
* anonymous Blob access is disabled
* Microsoft Entra ID and Managed Identity are used instead of embedded credentials
* RBAC is scoped to required Azure resources
* private AI outputs remain outside the public repository
* AI output requires human review

Advanced private networking is documented as future enterprise hardening rather than implemented for this small portfolio workload.

---

## Evaluation and Governance Results

The project uses three distinct validation layers:

```text
Structured Outputs
→ Is the response structurally valid?

Deterministic Validator
→ Does it satisfy explicit governance rules?

Semantic Evaluators
→ Is the statement actually supported by the cited evidence?
```

A custom governance regression suite included:

```text
Compliant response                  → PASS
Incomplete evidence coverage        → FAIL
Unsupported evidence association    → FAIL
```

All three expected outcomes were correctly classified.

---

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

Container Apps execution logs are captured in Azure Log Analytics.

Azure Cost Management is treated as the financial source of truth, and a monthly project budget alert is configured.

---

## Key Architecture Decisions

**No RAG**
The current problem uses structured, precomputed analytical context rather than an external knowledge corpus.

**No Agent**
The AI provides decision support but does not autonomously execute business actions.

**No Azure SQL**
The current workload does not justify another persistent database layer.

**No LLM-based KPI calculation**
Business metrics remain deterministic.

**Human review stays mandatory**
AI output remains decision support rather than an autonomous business decision.

---

## Repository Structure

```text
architecture/
    target architecture and architecture decisions

data/
    synthetic public examples only

docs/
    AI contracts, governance, evaluation and experiment documentation

prompts/
    versioned system prompts

src/ai/
    schemas, Foundry integration, boundary controls,
    validation and governed pipeline code

tests/
    synthetic validation, evaluation and pipeline evidence

screenshots/
    sanitized portfolio evidence

Dockerfile
requirements.txt
README.md
```

---

## Implemented

* business workflow analysis
* data profiling and quality controls
* canonical data model
* deterministic analytics
* regional analysis
* management dashboard
* AI context boundary
* Microsoft Foundry integration
* Structured Outputs
* deterministic AI validation
* semantic evaluation
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

## Future Enterprise Hardening

* Private Endpoints
* VNet-based isolation
* automated CI/CD
* infrastructure as code
* expanded production evaluation datasets

---

## Core Takeaway

This project treats AI as a governed reasoning layer on top of trusted deterministic analytics — not as a replacement for the data foundation.

**Trusted data → deterministic metrics → governed AI → validation → human review.**
