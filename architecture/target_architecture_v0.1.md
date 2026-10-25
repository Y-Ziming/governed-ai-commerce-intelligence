# Target Solution Architecture v0.1

## Governed AI Commerce Intelligence Platform

Status legend:

- ✅ BUILT — implemented and tested locally
- 🔵 NEXT BUILD — next implementation phase
- ⚪ FUTURE — designed but not yet required

---

## Architecture

```mermaid
flowchart TB

    %% =================================================
    %% SOURCES
    %% =================================================

    subgraph SOURCES["Business Data Sources"]
        S1["Commerce Order Data<br/>Excel / CSV<br/>✅ BUILT"]
        S2["EDI / API Sources<br/>⚪ FUTURE"]
        S3["Additional Marketplaces<br/>⚪ FUTURE"]
    end


    %% =================================================
    %% DATA PLATFORM
    %% =================================================

    subgraph DATA["Azure Data Platform"]

        RAW["Azure Storage / ADLS Gen2<br/>Raw Zone<br/>🔵 NEXT BUILD"]

        PIPE["Azure Container Apps Job<br/>Python Data Pipeline<br/><br/>Profiling<br/>Validation<br/>Canonical Transformation<br/>🔵 NEXT BUILD"]

        CURATED["Azure Storage / ADLS Gen2<br/>Curated + Analytics Zone<br/>🔵 NEXT BUILD"]

    end


    %% =================================================
    %% EXISTING ANALYTICS
    %% =================================================

    subgraph ANALYTICS["Trusted Analytics Layer"]

        CANONICAL["Canonical Data Model<br/><br/>Orders<br/>Order Lines<br/>Products<br/>Shipments<br/>✅ BUILT"]

        DQ["Data Quality Controls<br/>Quarantine / Reconciliation<br/>✅ BUILT"]

        MARTS["Analytics Marts<br/><br/>Monthly Sales<br/>Product Performance<br/>Regional Analytics<br/>✅ BUILT"]

    end


    %% =================================================
    %% APPLICATION
    %% =================================================

    subgraph APP["Decision Support Application"]

        DASH["Interactive Streamlit Dashboard<br/><br/>Product Drill-down<br/>Germany Map<br/>Regional Drill-down<br/>✅ BUILT"]

        CONTEXT["AI Context Builder<br/><br/>Trusted KPI JSON<br/>Evidence Package<br/>🔵 NEXT BUILD"]

        REVIEW["Human Review<br/><br/>Accept / Reject / Review Insight<br/>🔵 NEXT BUILD"]

    end


    %% =================================================
    %% AI
    %% =================================================

    subgraph AI["Microsoft Foundry"]

        FOUNDRY["Microsoft Foundry Resource<br/>+ Project<br/>🔵 NEXT BUILD"]

        MODEL["Model Deployment<br/>🔵 NEXT BUILD"]

        BRIEF["AI Management Brief<br/><br/>Summary<br/>Key Changes<br/>Drivers<br/>Risks<br/>Recommended Actions<br/>🔵 NEXT BUILD"]

        EVAL["Foundry Evaluation<br/><br/>Groundedness<br/>Relevance<br/>Numeric Consistency<br/>Safety<br/>🔵 NEXT BUILD"]
    end


    %% =================================================
    %% GOVERNANCE
    %% =================================================

    subgraph GOV["AI Governance & Security"]

        PII["PII / Sensitive Data Boundary<br/>✅ DESIGN PRINCIPLE"]

        VALIDATE["AI Output Validation<br/><br/>Schema Validation<br/>Evidence Check<br/>Numeric Consistency<br/>🔵 NEXT BUILD"]

        RISK["AI Risk Register<br/>System Card<br/>Human Oversight<br/>🔵 NEXT BUILD"]

        ID["Microsoft Entra ID<br/>Managed Identity<br/>Azure RBAC<br/>🔵 NEXT BUILD"]

        KV["Azure Key Vault<br/>Only for required external secrets<br/>🔵 NEXT BUILD"]
    end


    %% =================================================
    %% OPERATIONS
    %% =================================================

    subgraph OPS["Platform Engineering & Operations"]

        ACA["Azure Container Apps<br/>Dashboard / Application<br/>🔵 NEXT BUILD"]

        MON["Application Insights<br/>Azure Monitor<br/><br/>Latency<br/>Errors<br/>Token Usage<br/>Traces<br/>🔵 NEXT BUILD"]

        CICD["GitHub Actions<br/>+ Bicep Infrastructure as Code<br/>⚪ FUTURE"]

        COST["Cost Controls<br/><br/>Scale-to-zero<br/>Token Budget<br/>Model Selection<br/>Usage Monitoring<br/>🔵 NEXT BUILD"]
    end


    %% =================================================
    %% DATA FLOW
    %% =================================================

    S1 --> RAW
    S2 --> RAW
    S3 --> RAW

    RAW --> PIPE

    PIPE --> DQ
    DQ --> CANONICAL
    CANONICAL --> MARTS

    MARTS --> CURATED
    CURATED --> DASH

    DASH --> CONTEXT

    CONTEXT --> PII
    PII --> FOUNDRY

    FOUNDRY --> MODEL
    MODEL --> BRIEF

    BRIEF --> VALIDATE
    VALIDATE --> REVIEW
    REVIEW --> DASH

    MODEL --> EVAL
    EVAL --> RISK

    DASH -. deployment .-> ACA

    ACA -. identity .-> ID
    PIPE -. identity .-> ID
    FOUNDRY -. identity .-> ID

    ACA -. telemetry .-> MON
    FOUNDRY -. telemetry .-> MON

    KV -. secrets if required .-> ACA

    CICD -. deploy .-> ACA
    CICD -. provision .-> FOUNDRY

    MON --> COST