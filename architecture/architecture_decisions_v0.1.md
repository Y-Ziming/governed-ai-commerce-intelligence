# Architecture Decisions v0.1

## ADR-001 — Preserve deterministic analytics as the source of truth

Decision:
Business KPIs are calculated outside the LLM.

Reason:
Numeric accuracy, traceability and reproducibility are required.

---

## ADR-002 — Use Microsoft Foundry for the governed AI layer

Decision:
Microsoft Foundry will provide model access, evaluation and AI observability capabilities.

Reason:
The project specifically aims to demonstrate enterprise Azure AI architecture and governance experience.

---

## ADR-003 — Do not introduce RAG initially

Decision:
The first AI use case receives structured trusted KPI data directly.

Reason:
The use case does not require retrieval across a large unstructured knowledge base.

---

## ADR-004 — Do not introduce Azure SQL initially

Decision:
Use Azure Storage / ADLS for the first cloud MVP.

Reason:
Current data volume and access patterns do not justify an additional database layer.

---

## ADR-005 — Use Azure Container Apps

Decision:
Use Container Apps for the application and Container Apps Jobs for finite data-processing workloads.

Reason:
This supports containerized Python workloads while allowing consumption-based operation and scale-to-zero.

---

## ADR-006 — Use identity-based Azure access

Decision:
Use Microsoft Entra ID, Managed Identity and RBAC wherever supported.

Reason:
Avoid long-lived credentials and implement least-privilege access.