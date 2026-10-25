from pathlib import Path
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

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_FOLDER
    / "management_brief_programmatic_v0.1.json"
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
# 5. User request
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
#
# Local development authentication:
# DefaultAzureCredential -> Azure CLI login
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
# 7. Call gpt-5-mini through Responses API
# ==================================================

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


# ==================================================
# 8. Extract response text
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
# 9. Parse strict JSON
# ==================================================

try:

    management_brief = (
        json.loads(
            response_text
        )
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
# 10. Save model output
# ==================================================

with open(
    OUTPUT_FILE,
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
# 11. Usage information
# ==================================================

usage = getattr(
    response,
    "usage",
    None
)


print(
    "\nFoundry generation completed."
)

print(
    f"\nModel deployment:"
    f"\n{model_deployment}"
)

print(
    f"\nOutput:"
    f"\n{OUTPUT_FILE}"
)


if usage:

    print(
        "\nToken usage:"
    )

    print(
        f"Input tokens: "
        f"{getattr(usage, 'input_tokens', 'N/A')}"
    )

    print(
        f"Output tokens: "
        f"{getattr(usage, 'output_tokens', 'N/A')}"
    )

    print(
        f"Total tokens: "
        f"{getattr(usage, 'total_tokens', 'N/A')}"
    )


print(
    "\nIMPORTANT:"
)

print(
    "This run used synthetic data only."
)