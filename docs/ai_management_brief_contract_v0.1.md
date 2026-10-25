# AI Management Brief Contract v0.1

## 1. Purpose

The AI Management Brief converts trusted commerce analytics into a concise management-level interpretation.

The AI is used for:

- summarization
- interpretation
- prioritization
- highlighting changes
- identifying items requiring management attention
- suggesting possible follow-up actions

The AI is not the source of truth for business metrics.

---

## 2. Architecture Principle

Business metrics are calculated deterministically before they reach the AI layer.

The AI receives a curated evidence package produced by the trusted analytics layer.

```text
Raw Data
    ↓
Canonical Model
    ↓
Analytics
    ↓
Trusted KPI Context
    ↓
LLM
    ↓
Structured AI Brief
    ↓
Validation
    ↓
Human Review