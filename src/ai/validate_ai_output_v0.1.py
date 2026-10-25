from pathlib import Path
import argparse
import json
import sys


# ==================================================
# 1. Validation configuration
# ==================================================

EXPECTED_REPORT_STATUS = (
    "AI_DRAFT_REQUIRES_HUMAN_REVIEW"
)

EXPECTED_HUMAN_REVIEW_STATUS = (
    "PENDING"
)


ALLOWED_CONFIDENCE = {
    "HIGH",
    "MEDIUM",
    "LOW"
}


ALLOWED_ACTION_TYPES = {
    "INVESTIGATE",
    "REVIEW",
    "VERIFY",
    "MONITOR",
    "COMPARE"
}


ALLOWED_INSIGHT_CATEGORIES = {
    "OVERALL_PERFORMANCE",
    "PRODUCT",
    "REGION",
    "DATA_QUALITY",
    "METRIC_AVAILABILITY"
}


REQUIRED_TOP_LEVEL_FIELDS = {
    "contract_version",
    "reporting_period",
    "report_status",
    "executive_summary",
    "key_insights",
    "items_requiring_attention",
    "recommended_actions",
    "caveats",
    "used_evidence_refs",
    "human_review"
}


# ==================================================
# 2. Strict JSON loader
#
# Detects:
# - malformed JSON
# - duplicate JSON keys
# - trailing non-JSON content
# ==================================================

class DuplicateKeyError(ValueError):
    pass


def reject_duplicate_keys(pairs):

    result = {}

    for key, value in pairs:

        if key in result:

            raise DuplicateKeyError(
                f"Duplicate JSON key: {key}"
            )

        result[key] = value

    return result


def load_json_strict(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file,
            object_pairs_hook=(
                reject_duplicate_keys
            )
        )


# ==================================================
# 3. Evidence helpers
# ==================================================

def collect_context_evidence_ids(obj):
    """
    Recursively collect every explicit
    evidence_id contained in the trusted
    input context.
    """

    evidence_ids = set()

    if isinstance(obj, dict):

        for key, value in obj.items():

            if (
                key == "evidence_id"
                and isinstance(value, str)
                and value.strip()
            ):

                evidence_ids.add(
                    value.strip()
                )

            evidence_ids.update(
                collect_context_evidence_ids(
                    value
                )
            )

    elif isinstance(obj, list):

        for item in obj:

            evidence_ids.update(
                collect_context_evidence_ids(
                    item
                )
            )

    return evidence_ids


def collect_output_evidence_refs(obj):
    """
    Recursively collect all values appearing
    inside evidence_refs arrays in model output.
    """

    evidence_refs = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            if (
                key == "evidence_refs"
                and isinstance(value, list)
            ):

                for ref in value:

                    if isinstance(ref, str):

                        evidence_refs.append(
                            ref
                        )

            evidence_refs.extend(
                collect_output_evidence_refs(
                    value
                )
            )

    elif isinstance(obj, list):

        for item in obj:

            evidence_refs.extend(
                collect_output_evidence_refs(
                    item
                )
            )

    return evidence_refs


# ==================================================
# 4. Validation issue helper
# ==================================================

def add_issue(
    issues,
    code,
    path,
    message
):

    issues.append({
        "code": code,
        "path": path,
        "message": message
    })


# ==================================================
# 5. Basic field validators
# ==================================================

def validate_nonempty_string(
    value,
    path,
    issues
):

    if (
        not isinstance(value, str)
        or not value.strip()
    ):

        add_issue(
            issues,
            "INVALID_STRING",
            path,
            "Expected a non-empty string."
        )


def validate_evidence_refs(
    refs,
    path,
    valid_evidence_ids,
    issues
):
    """
    Every report item that exists must contain
    at least one valid evidence reference.
    """

    if not isinstance(refs, list):

        add_issue(
            issues,
            "INVALID_EVIDENCE_REFS_TYPE",
            path,
            "evidence_refs must be a list."
        )

        return


    if not refs:

        add_issue(
            issues,
            "EMPTY_EVIDENCE_REFS",
            path,
            (
                "Report item contains no "
                "evidence reference."
            )
        )

        return


    seen = set()


    for index, ref in enumerate(refs):

        ref_path = (
            f"{path}[{index}]"
        )

        if (
            not isinstance(ref, str)
            or not ref.strip()
        ):

            add_issue(
                issues,
                "INVALID_EVIDENCE_REFERENCE_TYPE",
                ref_path,
                (
                    "Evidence reference must "
                    "be a non-empty string."
                )
            )

            continue


        ref = ref.strip()


        if ref in seen:

            add_issue(
                issues,
                "DUPLICATE_EVIDENCE_REFERENCE",
                ref_path,
                (
                    f"Duplicate evidence "
                    f"reference: {ref}"
                )
            )


        seen.add(
            ref
        )


        if ref not in valid_evidence_ids:

            add_issue(
                issues,
                "UNKNOWN_EVIDENCE_REFERENCE",
                ref_path,
                (
                    f"Evidence ID does not "
                    f"exist in trusted context: "
                    f"{ref}"
                )
            )


# ==================================================
# 6. Validate executive summary
# ==================================================

def validate_executive_summary(
    summary,
    valid_evidence_ids,
    issues
):

    path = "executive_summary"


    if not isinstance(
        summary,
        dict
    ):

        add_issue(
            issues,
            "INVALID_SECTION_TYPE",
            path,
            "Executive summary must be an object."
        )

        return


    validate_nonempty_string(
        summary.get(
            "statement"
        ),
        f"{path}.statement",
        issues
    )


    validate_evidence_refs(
        summary.get(
            "evidence_refs"
        ),
        f"{path}.evidence_refs",
        valid_evidence_ids,
        issues
    )


# ==================================================
# 7. Validate insights
# ==================================================

def validate_key_insights(
    insights,
    valid_evidence_ids,
    issues
):

    path = "key_insights"


    if not isinstance(
        insights,
        list
    ):

        add_issue(
            issues,
            "INVALID_SECTION_TYPE",
            path,
            "key_insights must be a list."
        )

        return


    seen_ids = set()


    for index, item in enumerate(
        insights
    ):

        item_path = (
            f"{path}[{index}]"
        )


        if not isinstance(
            item,
            dict
        ):

            add_issue(
                issues,
                "INVALID_ITEM_TYPE",
                item_path,
                "Insight must be an object."
            )

            continue


        insight_id = item.get(
            "insight_id"
        )


        validate_nonempty_string(
            insight_id,
            f"{item_path}.insight_id",
            issues
        )


        if isinstance(
            insight_id,
            str
        ):

            if insight_id in seen_ids:

                add_issue(
                    issues,
                    "DUPLICATE_INSIGHT_ID",
                    f"{item_path}.insight_id",
                    (
                        f"Duplicate insight ID: "
                        f"{insight_id}"
                    )
                )

            seen_ids.add(
                insight_id
            )


        category = item.get(
            "category"
        )


        if category not in (
            ALLOWED_INSIGHT_CATEGORIES
        ):

            add_issue(
                issues,
                "INVALID_INSIGHT_CATEGORY",
                f"{item_path}.category",
                (
                    f"Invalid category: "
                    f"{category}"
                )
            )


        validate_nonempty_string(
            item.get(
                "statement"
            ),
            f"{item_path}.statement",
            issues
        )


        confidence = item.get(
            "confidence"
        )


        if confidence not in (
            ALLOWED_CONFIDENCE
        ):

            add_issue(
                issues,
                "INVALID_CONFIDENCE",
                f"{item_path}.confidence",
                (
                    f"Invalid confidence value: "
                    f"{confidence}"
                )
            )


        validate_evidence_refs(
            item.get(
                "evidence_refs"
            ),
            f"{item_path}.evidence_refs",
            valid_evidence_ids,
            issues
        )


# ==================================================
# 8. Validate attention items
# ==================================================

def validate_attention_items(
    items,
    valid_evidence_ids,
    issues
):

    path = (
        "items_requiring_attention"
    )


    if not isinstance(
        items,
        list
    ):

        add_issue(
            issues,
            "INVALID_SECTION_TYPE",
            path,
            (
                "items_requiring_attention "
                "must be a list."
            )
        )

        return


    seen_ids = set()


    for index, item in enumerate(
        items
    ):

        item_path = (
            f"{path}[{index}]"
        )


        if not isinstance(
            item,
            dict
        ):

            add_issue(
                issues,
                "INVALID_ITEM_TYPE",
                item_path,
                (
                    "Attention item must "
                    "be an object."
                )
            )

            continue


        attention_id = item.get(
            "attention_id"
        )


        validate_nonempty_string(
            attention_id,
            f"{item_path}.attention_id",
            issues
        )


        if isinstance(
            attention_id,
            str
        ):

            if attention_id in seen_ids:

                add_issue(
                    issues,
                    "DUPLICATE_ATTENTION_ID",
                    f"{item_path}.attention_id",
                    (
                        "Duplicate attention "
                        f"ID: {attention_id}"
                    )
                )

            seen_ids.add(
                attention_id
            )


        validate_nonempty_string(
            item.get(
                "statement"
            ),
            f"{item_path}.statement",
            issues
        )


        confidence = item.get(
            "confidence"
        )


        if confidence not in (
            ALLOWED_CONFIDENCE
        ):

            add_issue(
                issues,
                "INVALID_CONFIDENCE",
                f"{item_path}.confidence",
                (
                    f"Invalid confidence value: "
                    f"{confidence}"
                )
            )


        validate_evidence_refs(
            item.get(
                "evidence_refs"
            ),
            f"{item_path}.evidence_refs",
            valid_evidence_ids,
            issues
        )


# ==================================================
# 9. Validate recommended actions
# ==================================================

def validate_actions(
    actions,
    valid_evidence_ids,
    issues
):

    path = "recommended_actions"


    if not isinstance(
        actions,
        list
    ):

        add_issue(
            issues,
            "INVALID_SECTION_TYPE",
            path,
            (
                "recommended_actions "
                "must be a list."
            )
        )

        return


    seen_ids = set()


    for index, item in enumerate(
        actions
    ):

        item_path = (
            f"{path}[{index}]"
        )


        if not isinstance(
            item,
            dict
        ):

            add_issue(
                issues,
                "INVALID_ITEM_TYPE",
                item_path,
                "Action must be an object."
            )

            continue


        action_id = item.get(
            "action_id"
        )


        validate_nonempty_string(
            action_id,
            f"{item_path}.action_id",
            issues
        )


        if isinstance(
            action_id,
            str
        ):

            if action_id in seen_ids:

                add_issue(
                    issues,
                    "DUPLICATE_ACTION_ID",
                    f"{item_path}.action_id",
                    (
                        f"Duplicate action ID: "
                        f"{action_id}"
                    )
                )

            seen_ids.add(
                action_id
            )


        validate_nonempty_string(
            item.get(
                "action"
            ),
            f"{item_path}.action",
            issues
        )


        action_type = item.get(
            "action_type"
        )


        if action_type not in (
            ALLOWED_ACTION_TYPES
        ):

            add_issue(
                issues,
                "INVALID_ACTION_TYPE",
                f"{item_path}.action_type",
                (
                    f"Invalid action type: "
                    f"{action_type}"
                )
            )


        validate_evidence_refs(
            item.get(
                "evidence_refs"
            ),
            f"{item_path}.evidence_refs",
            valid_evidence_ids,
            issues
        )


# ==================================================
# 10. Validate caveats
# ==================================================

def validate_caveats(
    caveats,
    valid_evidence_ids,
    issues
):

    path = "caveats"


    if not isinstance(
        caveats,
        list
    ):

        add_issue(
            issues,
            "INVALID_SECTION_TYPE",
            path,
            "caveats must be a list."
        )

        return


    seen_ids = set()


    for index, item in enumerate(
        caveats
    ):

        item_path = (
            f"{path}[{index}]"
        )


        if not isinstance(
            item,
            dict
        ):

            add_issue(
                issues,
                "INVALID_ITEM_TYPE",
                item_path,
                "Caveat must be an object."
            )

            continue


        caveat_id = item.get(
            "caveat_id"
        )


        validate_nonempty_string(
            caveat_id,
            f"{item_path}.caveat_id",
            issues
        )


        if isinstance(
            caveat_id,
            str
        ):

            if caveat_id in seen_ids:

                add_issue(
                    issues,
                    "DUPLICATE_CAVEAT_ID",
                    f"{item_path}.caveat_id",
                    (
                        f"Duplicate caveat ID: "
                        f"{caveat_id}"
                    )
                )

            seen_ids.add(
                caveat_id
            )


        validate_nonempty_string(
            item.get(
                "statement"
            ),
            f"{item_path}.statement",
            issues
        )


        validate_evidence_refs(
            item.get(
                "evidence_refs"
            ),
            f"{item_path}.evidence_refs",
            valid_evidence_ids,
            issues
        )


# ==================================================
# 11. Main report validation
# ==================================================

def validate_report(
    context,
    report
):

    issues = []


    # ----------------------------------------------
    # Top-level JSON object
    # ----------------------------------------------

    if not isinstance(
        report,
        dict
    ):

        add_issue(
            issues,
            "INVALID_REPORT_TYPE",
            "root",
            "AI output must be a JSON object."
        )

        return issues


    # ----------------------------------------------
    # Required fields
    # ----------------------------------------------

    missing_fields = (

        REQUIRED_TOP_LEVEL_FIELDS
        - set(
            report.keys()
        )
    )


    for field in sorted(
        missing_fields
    ):

        add_issue(
            issues,
            "MISSING_REQUIRED_FIELD",
            field,
            (
                f"Required top-level field "
                f"is missing: {field}"
            )
        )


    # ----------------------------------------------
    # Contract version
    # ----------------------------------------------

    context_contract = (
        context.get(
            "contract_version"
        )
    )

    report_contract = (
        report.get(
            "contract_version"
        )
    )


    if (
        report_contract
        != context_contract
    ):

        add_issue(
            issues,
            "CONTRACT_VERSION_MISMATCH",
            "contract_version",
            (
                f"Context version is "
                f"{context_contract}; "
                f"report version is "
                f"{report_contract}."
            )
        )


    # ----------------------------------------------
    # Reporting period
    # ----------------------------------------------

    if (
        report.get(
            "reporting_period"
        )
        != context.get(
            "reporting_period"
        )
    ):

        add_issue(
            issues,
            "REPORTING_PERIOD_MISMATCH",
            "reporting_period",
            (
                "AI output reporting period "
                "does not match trusted context."
            )
        )


    # ----------------------------------------------
    # Report status
    # ----------------------------------------------

    if (
        report.get(
            "report_status"
        )
        != EXPECTED_REPORT_STATUS
    ):

        add_issue(
            issues,
            "INVALID_REPORT_STATUS",
            "report_status",
            (
                "Report status must be "
                f"{EXPECTED_REPORT_STATUS}."
            )
        )


    # ----------------------------------------------
    # Valid context evidence IDs
    # ----------------------------------------------

    valid_evidence_ids = (
        collect_context_evidence_ids(
            context
        )
    )


    if not valid_evidence_ids:

        add_issue(
            issues,
            "NO_CONTEXT_EVIDENCE",
            "context",
            (
                "Trusted context contains "
                "no evidence IDs."
            )
        )


    # ----------------------------------------------
    # Validate report sections
    # ----------------------------------------------

    validate_executive_summary(
        report.get(
            "executive_summary"
        ),
        valid_evidence_ids,
        issues
    )


    validate_key_insights(
        report.get(
            "key_insights"
        ),
        valid_evidence_ids,
        issues
    )


    validate_attention_items(
        report.get(
            "items_requiring_attention"
        ),
        valid_evidence_ids,
        issues
    )


    validate_actions(
        report.get(
            "recommended_actions"
        ),
        valid_evidence_ids,
        issues
    )


    validate_caveats(
        report.get(
            "caveats"
        ),
        valid_evidence_ids,
        issues
    )


    # ----------------------------------------------
    # Human review controls
    # ----------------------------------------------

    human_review = report.get(
        "human_review"
    )


    if not isinstance(
        human_review,
        dict
    ):

        add_issue(
            issues,
            "INVALID_HUMAN_REVIEW",
            "human_review",
            (
                "human_review must be "
                "an object."
            )
        )

    else:

        if (
            human_review.get(
                "required"
            )
            is not True
        ):

            add_issue(
                issues,
                "HUMAN_REVIEW_NOT_REQUIRED",
                "human_review.required",
                (
                    "human_review.required "
                    "must be true."
                )
            )


        if (
            human_review.get(
                "status"
            )
            != EXPECTED_HUMAN_REVIEW_STATUS
        ):

            add_issue(
                issues,
                "INVALID_HUMAN_REVIEW_STATUS",
                "human_review.status",
                (
                    "Initial human review "
                    "status must be PENDING."
                )
            )


    # ----------------------------------------------
    # used_evidence_refs
    # ----------------------------------------------

    used_evidence_refs = report.get(
        "used_evidence_refs"
    )


    if not isinstance(
        used_evidence_refs,
        list
    ):

        add_issue(
            issues,
            "INVALID_USED_EVIDENCE_REFS",
            "used_evidence_refs",
            (
                "used_evidence_refs "
                "must be a list."
            )
        )

    else:

        clean_used_refs = []


        for index, ref in enumerate(
            used_evidence_refs
        ):

            if (
                not isinstance(ref, str)
                or not ref.strip()
            ):

                add_issue(
                    issues,
                    "INVALID_USED_EVIDENCE_REFERENCE",
                    (
                        "used_evidence_refs"
                        f"[{index}]"
                    ),
                    (
                        "Reference must be "
                        "a non-empty string."
                    )
                )

                continue


            clean_used_refs.append(
                ref.strip()
            )


        if (
            len(clean_used_refs)
            != len(
                set(
                    clean_used_refs
                )
            )
        ):

            add_issue(
                issues,
                "DUPLICATE_USED_EVIDENCE_REFERENCE",
                "used_evidence_refs",
                (
                    "used_evidence_refs "
                    "contains duplicates."
                )
            )


        # Every listed used reference
        # must exist in trusted context.

        for ref in set(
            clean_used_refs
        ):

            if ref not in (
                valid_evidence_ids
            ):

                add_issue(
                    issues,
                    "UNKNOWN_USED_EVIDENCE_REFERENCE",
                    "used_evidence_refs",
                    (
                        f"Unknown evidence "
                        f"reference: {ref}"
                    )
                )


        # Compare declared evidence usage
        # against actual evidence_refs
        # used throughout the report.

        actual_refs = set(
            collect_output_evidence_refs(
                {
                    key: value
                    for key, value
                    in report.items()
                    if key
                    != "used_evidence_refs"
                }
            )
        )


        declared_refs = set(
            clean_used_refs
        )


        missing_from_declared = (

            actual_refs
            - declared_refs
        )


        extra_in_declared = (

            declared_refs
            - actual_refs
        )


        for ref in sorted(
            missing_from_declared
        ):

            add_issue(
                issues,
                "USED_EVIDENCE_REF_MISSING",
                "used_evidence_refs",
                (
                    f"{ref} is used in the "
                    "report but missing from "
                    "used_evidence_refs."
                )
            )


        for ref in sorted(
            extra_in_declared
        ):

            add_issue(
                issues,
                "UNUSED_EVIDENCE_REF_DECLARED",
                "used_evidence_refs",
                (
                    f"{ref} is declared as used "
                    "but is not referenced by "
                    "any report item."
                )
            )


    return issues


# ==================================================
# 12. Command-line interface
# ==================================================

parser = argparse.ArgumentParser(
    description=(
        "Deterministically validate an "
        "AI Management Brief against its "
        "trusted analytics context."
    )
)


parser.add_argument(
    "--context",
    required=True,
    help=(
        "Path to trusted AI input "
        "context JSON."
    )
)


parser.add_argument(
    "--output",
    required=True,
    help=(
        "Path to model-generated "
        "Management Brief JSON."
    )
)


parser.add_argument(
    "--report",
    required=False,
    help=(
        "Optional path for validation "
        "result JSON."
    )
)


args = parser.parse_args()


context_path = Path(
    args.context
)


output_path = Path(
    args.output
)


# ==================================================
# 13. Load files
# ==================================================

try:

    context = load_json_strict(
        context_path
    )

except Exception as error:

    print(
        "\nVALIDATION ERROR"
    )

    print(
        "\nTrusted context could "
        "not be loaded:"
    )

    print(
        str(error)
    )

    sys.exit(2)


try:

    report = load_json_strict(
        output_path
    )

except Exception as error:

    print(
        "\nVALIDATION FAIL"
    )

    print(
        "\nAI output is not valid "
        "strict JSON:"
    )

    print(
        str(error)
    )

    sys.exit(1)


# ==================================================
# 14. Run validation
# ==================================================

issues = validate_report(
    context,
    report
)


status = (
    "PASS"
    if not issues
    else "FAIL"
)


validation_result = {

    "validator_version":
        "0.1",

    "contract_version":
        context.get(
            "contract_version"
        ),

    "reporting_period":
        context.get(
            "reporting_period"
        ),

    "validation_status":
        status,

    "issue_count":
        len(
            issues
        ),

    "issues":
        issues
}


# ==================================================
# 15. Save validation report
# ==================================================

if args.report:

    report_path = Path(
        args.report
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            validation_result,
            file,
            ensure_ascii=False,
            indent=2
        )


# ==================================================
# 16. Console output
# ==================================================

print(
    "\n======================================"
)

print(
    "AI MANAGEMENT BRIEF VALIDATION"
)

print(
    "======================================"
)


print(
    f"\nValidator version: "
    f"{validation_result['validator_version']}"
)


print(
    f"Contract version: "
    f"{validation_result['contract_version']}"
)


print(
    f"Reporting period: "
    f"{validation_result['reporting_period']}"
)


print(
    f"\nVALIDATION {status}"
)


print(
    f"\nIssue count: "
    f"{len(issues)}"
)


if issues:

    print(
        "\nIssues:"
    )


    for number, issue in enumerate(
        issues,
        start=1
    ):

        print(
            f"\n{number}. "
            f"{issue['code']}"
        )

        print(
            f"   Path: "
            f"{issue['path']}"
        )

        print(
            f"   "
            f"{issue['message']}"
        )


else:

    print(
        "\nAll deterministic "
        "validation controls passed."
    )


if args.report:

    print(
        f"\nValidation report:"
        f"\n{args.report}"
    )


print(
    "\n======================================"
)


# ==================================================
# 17. Process exit code
#
# 0 = PASS
# 1 = validation failure
# 2 = technical/input failure
#
# Useful later for CI/CD release gates.
# ==================================================

if issues:

    sys.exit(1)


sys.exit(0)