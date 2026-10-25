from pathlib import Path
from datetime import datetime, timezone
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


# ==================================================
# 1. Project paths
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

CONTEXT_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic"
    / "management_brief_input_example_v0.2.json"
)

GENERATION_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_generation"
    / "results"
)

VALIDATION_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_validation"
    / "results"
)

OBSERVABILITY_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_observability"
)

PIPELINE_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_pipeline"
    / "results"
)

VALIDATOR_FILE = (
    PROJECT_ROOT
    / "src"
    / "ai"
    / "validate_ai_output_v0.1.py"
)

USAGE_LOG_FILE = (
    OBSERVABILITY_FOLDER
    / "ai_usage_log_v0.1.csv"
)


for folder in [
    GENERATION_FOLDER,
    VALIDATION_FOLDER,
    OBSERVABILITY_FOLDER,
    PIPELINE_FOLDER,
]:

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )


# ==================================================
# 2. Configuration
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

DATA_CLASSIFICATION = "SYNTHETIC"

OPERATION_TYPE = (
    "MANAGEMENT_BRIEF_GENERATION"
)


# ==================================================
# 3. Load prompt
# ==================================================

system_prompt = (
    PROMPT_FILE
    .read_text(
        encoding="utf-8"
    )
)


# ==================================================
# 4. Load trusted synthetic context
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
    indent=2,
)


# ==================================================
# 5. Build request
# ==================================================

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
# 6. Connect to Microsoft Foundry
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
# 7. Call model with Structured Outputs
# ==================================================

run_started_at = datetime.now(
    timezone.utc
)


print(
    "\nCalling Microsoft Foundry..."
)

print(
    "Structured output schema: "
    f"{SCHEMA_VERSION}"
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
        "\nFoundry structured-output "
        "call failed:"
    )

    print(
        str(error)
    )

    sys.exit(1)


run_completed_at = datetime.now(
    timezone.utc
)


# ==================================================
# 8. Extract parsed structured output
# ==================================================

management_brief = (
    response.output_parsed
)


if management_brief is None:

    print(
        "\nSTRUCTURED OUTPUT: FAIL"
    )

    print(
        "Foundry returned no parsed "
        "ManagementBrief object."
    )

    if response.output_text:

        print(
            "\nRaw response:"
        )

        print(
            response.output_text
        )

    sys.exit(1)


print(
    "\nSTRUCTURED OUTPUT: PASS"
)


# ==================================================
# 9. Convert Pydantic object to JSON-safe dict
# ==================================================

management_brief_dict = (
    management_brief
    .model_dump(
        mode="json"
    )
)


# ==================================================
# 10. Create timestamped filenames
# ==================================================

timestamp_label = (
    run_started_at
    .strftime(
        "%Y%m%dT%H%M%SZ"
    )
)


generation_file = (
    GENERATION_FOLDER
    / (
        "management_brief_structured_"
        f"{timestamp_label}.json"
    )
)


validation_report_file = (
    VALIDATION_FOLDER
    / (
        "management_brief_validation_"
        f"{timestamp_label}.json"
    )
)


pipeline_summary_file = (
    PIPELINE_FOLDER
    / (
        "management_brief_pipeline_"
        f"{timestamp_label}.json"
    )
)


# ==================================================
# 11. Save structured model output
# ==================================================

with open(
    generation_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        management_brief_dict,
        file,
        ensure_ascii=False,
        indent=2,
    )


# ==================================================
# 12. Token telemetry
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
        OPERATION_TYPE,

    "model_deployment":
        model_deployment,

    "prompt_version":
        PROMPT_VERSION,

    "contract_version":
        CONTRACT_VERSION,

    "data_classification":
        DATA_CLASSIFICATION,

    "input_tokens":
        input_tokens,

    "output_tokens":
        output_tokens,

    "total_tokens":
        total_tokens,

    "duration_seconds":
        duration_seconds,

    "response_id":
        getattr(
            response,
            "id",
            None,
        ),

    "generation_status":
        "SUCCESS",
}


fieldnames = list(
    telemetry_record.keys()
)


file_exists = (
    USAGE_LOG_FILE.exists()
)


with open(
    USAGE_LOG_FILE,
    "a",
    newline="",
    encoding="utf-8-sig",
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
    )

    if not file_exists:

        writer.writeheader()

    writer.writerow(
        telemetry_record
    )


# ==================================================
# 13. Run deterministic validator
# ==================================================

print(
    "\nRunning deterministic "
    "governance validator..."
)


validator_command = [

    sys.executable,

    str(
        VALIDATOR_FILE
    ),

    "--context",
    str(
        CONTEXT_FILE
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
# 14. Pipeline summary
# ==================================================

pipeline_summary = {

    "pipeline_version":
        "management_brief_pipeline_v0.1",

    "timestamp_utc":
        run_started_at.isoformat(),

    "model_deployment":
        model_deployment,

    "prompt_version":
        PROMPT_VERSION,

    "schema_version":
        SCHEMA_VERSION,

    "contract_version":
        CONTRACT_VERSION,

    "data_classification":
        DATA_CLASSIFICATION,

    "structured_output_status":
        "PASS",

    "deterministic_validation_status":
        validation_status,

    "pipeline_status":
        pipeline_status,

    "input_tokens":
        input_tokens,

    "output_tokens":
        output_tokens,

    "total_tokens":
        total_tokens,

    "duration_seconds":
        duration_seconds,

    "generation_file":
        str(
            generation_file.relative_to(
                PROJECT_ROOT
            )
        ),

    "validation_report_file":
        str(
            validation_report_file.relative_to(
                PROJECT_ROOT
            )
        ),

    "human_review_required":
        True,
}


with open(
    pipeline_summary_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        pipeline_summary,
        file,
        ensure_ascii=False,
        indent=2,
    )


# ==================================================
# 15. Final result
# ==================================================

print(
    "\n================================"
)

print(
    "MANAGEMENT BRIEF PIPELINE RESULT"
)

print(
    "================================"
)


print(
    "\nStructured output: PASS"
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
    f"Duration seconds: "
    f"{duration_seconds}"
)


print(
    f"\nGeneration:"
    f"\n{generation_file}"
)


print(
    f"\nValidation report:"
    f"\n{validation_report_file}"
)


print(
    f"\nPipeline summary:"
    f"\n{pipeline_summary_file}"
)


print(
    "\nHuman review required: YES"
)


if pipeline_status == "PASS":

    sys.exit(0)


if pipeline_status == "BLOCKED":

    sys.exit(1)


sys.exit(2)