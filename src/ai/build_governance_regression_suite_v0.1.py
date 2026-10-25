from pathlib import Path
import json


# ==================================================
# 1. Project paths
# ==================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

SYNTHETIC_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
)

OUTPUT_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_evaluation"
    / "datasets"
)

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


CONTEXT_FILE = (
    SYNTHETIC_FOLDER
    / "management_brief_input_example_v0.2.json"
)

OUTPUT_FILE = (
    OUTPUT_FOLDER
    / "governance_regression_suite_v0.1.jsonl"
)


# ==================================================
# 2. Load trusted synthetic context
# ==================================================

with open(
    CONTEXT_FILE,
    "r",
    encoding="utf-8"
) as file:

    trusted_context = json.load(
        file
    )


context_text = json.dumps(
    trusted_context,
    ensure_ascii=False,
    indent=2
)


# ==================================================
# 3. Evaluation query
# ==================================================

query = (
    "Generate an evidence-grounded management brief "
    "from the supplied trusted analytics context. "
    "Every material statement must be fully supported "
    "by its cited evidence. Do not create unsupported "
    "associations between separate facts."
)


# ==================================================
# 4. CASE 1
# Expected PASS
#
# Complete evidence coverage.
# No unsupported association.
# ==================================================

case_pass = {

    "case_id":
        "CASE_GOV_PASS_001",

    "case_description":
        "Complete evidence support with no unsupported association.",

    "expected_result":
        "PASS",

    "expected_issue":
        "NONE",

    "query":
        query,

    "context":
        context_text,

    "response":
        json.dumps(
            {
                "key_insights": [
                    {
                        "statement": (
                            "Compared with 2026-07, "
                            "order count increased from "
                            "110 to 120 "
                            "(order_change_pct 9.1) "
                            "and units sold increased "
                            "from 116 to 128 "
                            "(units_change_pct 10.3)."
                        ),
                        "evidence_refs": [
                            "EV_OVERALL_001",
                            "EV_PERIOD_001"
                        ]
                    }
                ],
                "recommended_actions": [
                    {
                        "action": (
                            "Monitor PRODUCT_B's "
                            "reported decline in "
                            "subsequent reporting periods "
                            "before considering operational "
                            "changes."
                        ),
                        "evidence_refs": [
                            "EV_PRODUCT_002"
                        ]
                    }
                ]
            },
            ensure_ascii=False,
            indent=2
        )
}


# ==================================================
# 5. CASE 2
# Expected FAIL
#
# Same factual statement as Case 1, but current
# period values 120 / 128 are not covered by
# EV_PERIOD_001.
# ==================================================

case_evidence_incomplete = {

    "case_id":
        "CASE_GOV_FAIL_EVIDENCE_001",

    "case_description":
        "Current-period facts are stated without citing their evidence record.",

    "expected_result":
        "FAIL",

    "expected_issue":
        "EVIDENCE_INSUFFICIENCY",

    "query":
        query,

    "context":
        context_text,

    "response":
        json.dumps(
            {
                "key_insights": [
                    {
                        "statement": (
                            "Compared with 2026-07, "
                            "order count increased from "
                            "110 to 120 "
                            "(order_change_pct 9.1) "
                            "and units sold increased "
                            "from 116 to 128 "
                            "(units_change_pct 10.3)."
                        ),
                        "evidence_refs": [
                            "EV_PERIOD_001"
                        ]
                    }
                ]
            },
            ensure_ascii=False,
            indent=2
        )
}


# ==================================================
# 6. CASE 3
# Expected FAIL
#
# Missing quantity exists, but context does not
# identify which product is affected.
# ==================================================

case_unsupported_association = {

    "case_id":
        "CASE_GOV_FAIL_ASSOCIATION_001",

    "case_description":
        "General missing-quantity issue is incorrectly associated with specific products.",

    "expected_result":
        "FAIL",

    "expected_issue":
        "UNSUPPORTED_ASSOCIATION",

    "query":
        query,

    "context":
        context_text,

    "response":
        json.dumps(
            {
                "recommended_actions": [
                    {
                        "action": (
                            "Because one order line has "
                            "a missing quantity, verify "
                            "PRODUCT_A, PRODUCT_B and "
                            "PRODUCT_C because their "
                            "reported changes may be "
                            "data artifacts."
                        ),
                        "evidence_refs": [
                            "EV_DQ_001",
                            "EV_PRODUCT_001",
                            "EV_PRODUCT_002",
                            "EV_PRODUCT_003"
                        ]
                    }
                ]
            },
            ensure_ascii=False,
            indent=2
        )
}


# ==================================================
# 7. Write JSONL
# ==================================================

cases = [
    case_pass,
    case_evidence_incomplete,
    case_unsupported_association
]


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    for case in cases:

        file.write(
            json.dumps(
                case,
                ensure_ascii=False
            )
        )

        file.write(
            "\n"
        )


# ==================================================
# 8. Console output
# ==================================================

print(
    "\nGovernance regression suite created."
)

print(
    f"\nCase count: {len(cases)}"
)

print(
    "\nExpected outcomes:"
)

for case in cases:

    print(
        f"- {case['case_id']}: "
        f"{case['expected_result']} "
        f"({case['expected_issue']})"
    )


print(
    f"\nDataset:"
    f"\n{OUTPUT_FILE}"
)

print(
    "\nNo real company data was used."
)