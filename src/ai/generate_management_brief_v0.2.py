from pathlib import Path
from datetime import datetime, timezone
import csv
import json
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


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

OUTPUT_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_generation"
    / "results"
)

TELEMETRY_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_observability"
)

USAGE_LOG_FILE = (
    TELEMETRY_FOLDER
    / "ai_usage_log_v0.1.csv"
)


OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

TELEMETRY_FOLDER.mkdir(
    parents=True,
    exist_ok=True
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

CONTRACT_VERSION = "0.2"

DATA_CLASSIFICATION = "SYNTHETIC"

OPERATION_TYPE = "MANAGEMENT_BRIEF_GENERATION"


# ==================================================
# 3. Load system prompt
# ==================================================

system_prompt = (
    PROMPT_FILE
    .read_text(
        encoding="utf-8"
    )
)


# ==================================================
# 4. Load synthetic trusted context
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
# 5. Build user request
# ==================================================

user_input = (
    "Generate a management brief from the "
    "following trusted analytics context.\n\n"
    "Follow the system instructions exactly.\n\n"
    "Return valid JSON only.\n\n"
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
# 7. Call model
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
        .create(
            model=model_deployment,
            instructions=system_prompt,
            input=user_input
        )
    )

except Exception as error:

    print(
        "\nFoundry call failed:"
    )

    print(
        str(error)
    )

    sys.exit(1)


run_completed_at = datetime.now(
    timezone.utc
)


# ==================================================
# 8. Extract response
# ==================================================

response_text = (
    response.output_text
)


if (
    not response_text
    or not response_text.strip()
):

    raise ValueError(
        "Foundry returned no output text."
    )


# ==================================================
# 9. Parse JSON
# ==================================================

try:

    management_brief = json.loads(
        response_text
    )

except json.JSONDecodeError as error:

    print(
        "\nModel response was not valid JSON."
    )

    print(
        str(error)
    )

    print(
        "\nRaw response:"
    )

    print(
        response_text
    )

    sys.exit(1)


# ==================================================
# 10. Create unique output filename
# ==================================================

timestamp_label = (
    run_started_at
    .strftime(
        "%Y%m%dT%H%M%SZ"
    )
)


output_file = (
    OUTPUT_FOLDER
    / (
        "management_brief_programmatic_"
        f"{timestamp_label}.json"
    )
)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        management_brief,
        file,
        ensure_ascii=False,
        indent=2
    )


# ==================================================
# 11. Read token usage
# ==================================================

usage = getattr(
    response,
    "usage",
    None
)


input_tokens = (
    getattr(
        usage,
        "input_tokens",
        None
    )
    if usage
    else None
)


output_tokens = (
    getattr(
        usage,
        "output_tokens",
        None
    )
    if usage
    else None
)


total_tokens = (
    getattr(
        usage,
        "total_tokens",
        None
    )
    if usage
    else None
)


# ==================================================
# 12. Calculate request duration
# ==================================================

duration_seconds = round(
    (
        run_completed_at
        - run_started_at
    ).total_seconds(),
    3
)


# ==================================================
# 13. Build telemetry record
# ==================================================

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
            None
        ),

    "generation_status":
        "SUCCESS"
}


# ==================================================
# 14. Append telemetry CSV
# ==================================================

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
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    if not file_exists:

        writer.writeheader()

    writer.writerow(
        telemetry_record
    )


# ==================================================
# 15. Console output
# ==================================================

print(
    "\nFoundry generation completed."
)


print(
    f"\nModel deployment:"
    f"\n{model_deployment}"
)


print(
    f"\nOutput:"
    f"\n{output_file}"
)


print(
    "\nToken usage:"
)


print(
    f"Input tokens: "
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
    f"\nDuration seconds: "
    f"{duration_seconds}"
)


print(
    f"\nUsage telemetry:"
    f"\n{USAGE_LOG_FILE}"
)


print(
    "\nIMPORTANT:"
)

print(
    "This run used synthetic data only."
)