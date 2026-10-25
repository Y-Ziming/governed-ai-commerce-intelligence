from typing import Literal

from pydantic import BaseModel, ConfigDict


# ==================================================
# Shared types
# ==================================================

ConfidenceLevel = Literal[
    "HIGH",
    "MEDIUM",
    "LOW",
]

InsightCategory = Literal[
    "OVERALL_PERFORMANCE",
    "PRODUCT",
    "REGION",
    "DATA_QUALITY",
    "METRIC_AVAILABILITY",
]

ActionType = Literal[
    "INVESTIGATE",
    "REVIEW",
    "VERIFY",
    "MONITOR",
    "COMPARE",
]


# ==================================================
# Base model
# ==================================================

class StrictModel(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )


# ==================================================
# Output objects
# ==================================================

class ExecutiveSummary(StrictModel):

    statement: str
    evidence_refs: list[str]


class KeyInsight(StrictModel):

    insight_id: str
    category: InsightCategory
    statement: str
    confidence: ConfidenceLevel
    evidence_refs: list[str]


class AttentionItem(StrictModel):

    attention_id: str
    statement: str
    confidence: ConfidenceLevel
    evidence_refs: list[str]


class RecommendedAction(StrictModel):

    action_id: str
    action: str
    action_type: ActionType
    evidence_refs: list[str]


class Caveat(StrictModel):

    caveat_id: str
    statement: str
    evidence_refs: list[str]


class HumanReview(StrictModel):

    required: Literal[True]
    status: Literal["PENDING"]


# ==================================================
# Management Brief contract
# ==================================================

class ManagementBrief(StrictModel):

    contract_version: Literal["0.2"]

    reporting_period: str

    report_status: Literal[
        "AI_DRAFT_REQUIRES_HUMAN_REVIEW"
    ]

    executive_summary: ExecutiveSummary

    key_insights: list[KeyInsight]

    items_requiring_attention: list[AttentionItem]

    recommended_actions: list[RecommendedAction]

    caveats: list[Caveat]

    used_evidence_refs: list[str]

    human_review: HumanReview