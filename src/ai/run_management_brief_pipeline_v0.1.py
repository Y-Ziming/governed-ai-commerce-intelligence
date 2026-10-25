from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import json
import os
import subprocess
import sys

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from management_brief_schema_v0_2 import (
    ManagementBrief,
)

from cloud_context_boundary_v0_1 import (
    path_is_inside,
    validate_cloud_context,
)


# ==================================================
# 1. Project
# ==================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

PROMPT_FILE = (
    PROJECT_ROOT
    / "prompts"
    / "management_brief_system_v0.2.md"
)

VALIDATOR_FILE = (
    PROJECT_ROOT
    / "src"
    / "ai"
    / "validate_ai_output_v0.1.py"
)


# ==================================================
# 2. CLI
# ==================================================

parser = argparse.ArgumentParser(
    description=(
        "Run the governed Management Brief "
        "generation pipeline."
    )
)

parser.add_argument(
    "--context",
    required=True,
    help="Trusted analytics context JSON file.",
)

parser.add_argument(
    "--output-root",
    required=True,
    help="Root directory for generated artifacts.",
)

parser.add_argument(
    "--data-classification",
    required=True,
    choices=[
        "SYNTHETIC",
        "PRIVATE_AGGREGATED",
    ],
)

args = parser.parse_args()


context_file = Path(
    args.context
).resolve()

output_root = Path(
    args.output_root
).resolve()


# ==================================================
# 3. Safety checks
# ==================================================

if not context_file.exists():

    raise FileNotFoundError(
        f"Context file not found: "
        f"{context_file}"
    )


# PRIVATE artifacts must never be written
# inside the public portfolio repository.

if (
    args.data_classification
    == "PRIVATE_AGGREGATED"
    and path_is_inside(
        output_root,
        PROJECT_ROOT,
    )
):

    print(
        "\nPIPELINE BLOCKED"
    )

    print(
        "PRIVATE_AGGREGATED output "
        "cannot be written inside the "
        "public portfolio repository."
    )

    sys.exit(1)


# ==================================================
# 4. Output folders
# ==================================================

generation_folder = (
    output_root
    / "generation"
)

validation_folder = (
    output_root
    / "validation"
)

pipeline_folder = (
    output_root
    / "pipeline"
)

observability_folder = (
    output_root
    / "observability"
)


for folder in [
    generation_folder,
    validation_folder,
    pipeline_folder,
    observability_folder,
]:

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )


# ==================================================
# 5. Load trusted context
# ==================================================

with open(
    context_file,
    "r",
    encoding="utf-8",
) as file:

    trusted_context = json.load(
        file
    )


# ==================================================
# 6. Cloud boundary gate
# ==================================================

boundary_violations = (
    validate_cloud_context(
        trusted_context
    )
)


print(
    "\nRunning cloud context boundary check..."
)


if boundary_violations:

    print(
        "\nCLOUD CONTEXT BOUNDARY: FAIL"
    )

    print(
        f"Violation count: "
        f"{len(boundary_violations)}"
    )

    for violation in boundary_violations:

        print(
            f"- {violation}"
        )

    print(
        "\nNo data was sent to "
        "Microsoft Foundry."
    )

    sys.exit(1)


print(
    "CLOUD CONTEXT BOUNDARY: PASS"
)


# ==================================================
# 7. Configuration
# ==================================================

project_endpoint = os.getenv(
    "FOUNDRY_PROJECT_ENDPOINT"
)

model_deployment = os.getenv(
    "FOUNDRY_MODEL_DEPLOYMENT"
)


if not project_endpoint:

    raise ValueError(
        "FOUNDRY_PROJECT_ENDPOINT "
        "environment variable is missing."
    )


if not model_deployment:

    raise ValueError(
        "FOUNDRY_MODEL_DEPLOYMENT "
        "environment variable is missing."
    )


PROMPT_VERSION = (
    "management_brief_system_v0.2"
)

SCHEMA_VERSION = (
    "management_brief_schema_v0.2"
)

CONTRACT_VERSION = "0.2"


# ==================================================
# 8. Load prompt
# ==================================================

system_prompt = (
    PROMPT_FILE
    .read_text(
        encoding="utf-8"
    )
)


context_text = json.dumps(
    trusted_context,
    ensure_ascii=False,
    indent=2,
)


user_input = (
    "Generate a management brief from the "
    "following trusted analytics context.\n\n"
    "Follow the system instructions exactly.\n\n"
    "Use only evidence contained in the "
    "trusted analytics context.\n\n"
    "Trusted analytics context:\n\n"
    f"{context_text}"
)


# ==================================================
# 9. Foundry connection
# ==================================================

credential = DefaultAzureCredential()


project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=credential,
)


openai_client = (
    project_client
    .get_openai_client()
)


# ==================================================
# 10. Structured generation
# ==================================================

run_started_at = datetime.now(
    timezone.utc
)


print(
    "\nCalling Microsoft Foundry..."
)


try:

    response = (
        openai_client
        .responses
        .parse(
            model=model_deployment,
            instructions=system_prompt,
            input=user_input,
            text_format=ManagementBrief,
        )
    )

except Exception as error:

    print(
        "\nFOUNDRY CALL: FAIL"
    )

    print(
        str(error)
    )

    sys.exit(2)


run_completed_at = datetime.now(
    timezone.utc
)


management_brief = (
    response.output_parsed
)


if management_brief is None:

    print(
        "\nSTRUCTURED OUTPUT: FAIL"
    )

    sys.exit(1)


print(
    "STRUCTURED OUTPUT: PASS"
)


management_brief_dict = (
    management_brief.model_dump(
        mode="json"
    )
)
# ==================================================
# Derive used_evidence_refs deterministically
#
# Do not trust the LLM to maintain this redundant
# summary field. It can be calculated exactly from
# all evidence_refs contained in the report.
# ==================================================

def collect_evidence_refs(value):

    refs = set()

    if isinstance(value, dict):

        for key, child in value.items():

            if (
                key == "evidence_refs"
                and isinstance(child, list)
            ):

                for ref in child:

                    if isinstance(ref, str):

                        refs.add(
                            ref.strip()
                        )

            else:

                refs.update(
                    collect_evidence_refs(
                        child
                    )
                )

    elif isinstance(value, list):

        for child in value:

            refs.update(
                collect_evidence_refs(
                    child
                )
            )

    return refs


derived_evidence_refs = sorted(
    collect_evidence_refs(
        management_brief_dict
    )
)


management_brief_dict[
    "used_evidence_refs"
] = derived_evidence_refs

# ==================================================
# 11. Artifact filenames
# ==================================================

timestamp_label = (
    run_started_at.strftime(
        "%Y%m%dT%H%M%SZ"
    )
)


generation_file = (
    generation_folder
    / (
        "management_brief_"
        f"{timestamp_label}.json"
    )
)


validation_report_file = (
    validation_folder
    / (
        "management_brief_validation_"
        f"{timestamp_label}.json"
    )
)


pipeline_summary_file = (
    pipeline_folder
    / (
        "management_brief_pipeline_"
        f"{timestamp_label}.json"
    )
)


usage_log_file = (
    observability_folder
    / "ai_usage_log_v0.1.csv"
)


# ==================================================
# 12. Save generated brief
# ==================================================

with open(
    generation_file,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        management_brief_dict,
        file,
        ensure_ascii=False,
        indent=2,
    )


# ==================================================
# 13. Usage telemetry
# ==================================================

usage = getattr(
    response,
    "usage",
    None,
)


input_tokens = (
    getattr(
        usage,
        "input_tokens",
        None,
    )
    if usage
    else None
)


output_tokens = (
    getattr(
        usage,
        "output_tokens",
        None,
    )
    if usage
    else None
)


total_tokens = (
    getattr(
        usage,
        "total_tokens",
        None,
    )
    if usage
    else None
)


duration_seconds = round(
    (
        run_completed_at
        - run_started_at
    ).total_seconds(),
    3,
)


telemetry_record = {

    "timestamp_utc":
        run_started_at.isoformat(),

    "operation_type":
        "MANAGEMENT_BRIEF_GENERATION",

    "model_deployment":
        model_deployment,

    "prompt_version":
        PROMPT_VERSION,

    "contract_version":
        CONTRACT_VERSION,

    "data_classification":
        args.data_classification,

    "input_tokens":
        input_tokens,

    "output_tokens":
        output_tokens,

    "total_tokens":
        total_tokens,

    "duration_seconds":
        duration_seconds,

    "generation_status":
        "SUCCESS",
}


file_exists = (
    usage_log_file.exists()
)


with open(
    usage_log_file,
    "a",
    newline="",
    encoding="utf-8-sig",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=list(
            telemetry_record.keys()
        ),
    )

    if not file_exists:

        writer.writeheader()

    writer.writerow(
        telemetry_record
    )


# ==================================================
# 14. Deterministic validator
# ==================================================

print(
    "\nRunning deterministic validator..."
)


validator_command = [

    sys.executable,

    str(
        VALIDATOR_FILE
    ),

    "--context",
    str(
        context_file
    ),

    "--output",
    str(
        generation_file
    ),

    "--report",
    str(
        validation_report_file
    ),
]


validator_result = subprocess.run(
    validator_command,
    capture_output=True,
    text=True,
)


if validator_result.stdout:

    print(
        validator_result.stdout
    )


if validator_result.stderr:

    print(
        validator_result.stderr
    )


if validator_result.returncode == 0:

    validation_status = "PASS"
    pipeline_status = "PASS"

elif validator_result.returncode == 1:

    validation_status = "FAIL"
    pipeline_status = "BLOCKED"

else:

    validation_status = (
        "TECHNICAL_ERROR"
    )

    pipeline_status = (
        "TECHNICAL_ERROR"
    )


# ==================================================
# 15. Pipeline summary
# ==================================================

pipeline_summary = {

    "pipeline_version":
        "management_brief_pipeline_v0.2",

    "timestamp_utc":
        run_started_at.isoformat(),

    "data_classification":
        args.data_classification,

    "cloud_context_boundary":
        "PASS",

    "structured_output_status":
        "PASS",

    "deterministic_validation_status":
        validation_status,

    "pipeline_status":
        pipeline_status,

    "model_deployment":
        model_deployment,

    "prompt_version":
        PROMPT_VERSION,

    "schema_version":
        SCHEMA_VERSION,

    "contract_version":
        CONTRACT_VERSION,

    "input_tokens":
        input_tokens,

    "output_tokens":
        output_tokens,

    "total_tokens":
        total_tokens,

    "duration_seconds":
        duration_seconds,

    "human_review_required":
        True,
}


with open(
    pipeline_summary_file,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        pipeline_summary,
        file,
        ensure_ascii=False,
        indent=2,
    )


# ==================================================
# 16. Result
# ==================================================

print(
    "\n================================"
)

print(
    "GOVERNED AI PIPELINE RESULT"
)

print(
    "================================"
)


print(
    "\nCloud context boundary: PASS"
)


print(
    "Structured output: PASS"
)


print(
    "Deterministic validation: "
    f"{validation_status}"
)


print(
    "Pipeline status: "
    f"{pipeline_status}"
)


print(
    "\nData classification: "
    f"{args.data_classification}"
)


print(
    f"\nInput tokens: "
    f"{input_tokens}"
)


print(
    f"Output tokens: "
    f"{output_tokens}"
)


print(
    f"Total tokens: "
    f"{total_tokens}"
)


print(
    f"\nOutput root:"
    f"\n{output_root}"
)


print(
    "\nHuman review required: YES"
)


if pipeline_status == "PASS":

    sys.exit(0)

elif pipeline_status == "BLOCKED":

    sys.exit(1)

else:

    sys.exit(2)