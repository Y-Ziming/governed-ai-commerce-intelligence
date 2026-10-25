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

EVALUATION_FOLDER = (
    PROJECT_ROOT
    / "tests"
    / "ai_evaluation"
    / "datasets"
)

EVALUATION_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


INPUT_CONTEXT_FILE = (
    SYNTHETIC_FOLDER
    / "management_brief_input_example_v0.2.json"
)

MODEL_OUTPUT_FILE = (
    SYNTHETIC_FOLDER
    / "management_brief_output_gpt5mini_v0.2.json"
)

OUTPUT_DATASET_FILE = (
    EVALUATION_FOLDER
    / "semantic_eval_dataset_v0.1.jsonl"
)


# ==================================================
# 2. Load synthetic trusted context
# ==================================================

with open(
    INPUT_CONTEXT_FILE,
    "r",
    encoding="utf-8"
) as file:

    trusted_context = json.load(
        file
    )


# ==================================================
# 3. Load model response
# ==================================================

with open(
    MODEL_OUTPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    model_response = json.load(
        file
    )


# ==================================================
# 4. Evaluation query
# ==================================================

query = (
    "Generate a management brief from the "
    "supplied trusted analytics context. "
    "Use only information contained in the "
    "context. Do not invent metrics, causal "
    "explanations or unsupported relationships. "
    "The output is decision support and requires "
    "human review."
)


# ==================================================
# 5. Build one evaluation record
#
# Foundry built-in quality evaluators use:
#
# query    → user task
# context  → trusted source information
# response → model-generated answer
#
# Extra metadata is retained for traceability.
# ==================================================

evaluation_record = {

    "case_id":
        "CASE_BASELINE_001",

    "query":
        query,

    "context":
        json.dumps(
            trusted_context,
            ensure_ascii=False,
            indent=2
        ),

    "response":
        json.dumps(
            model_response,
            ensure_ascii=False,
            indent=2
        ),

    "model":
        "gpt-5-mini",

    "contract_version":
        "0.2",

    "prompt_version":
        "management_brief_system_v0.2",

    "dataset_version":
        "semantic_eval_dataset_v0.1"
}


# ==================================================
# 6. Write JSONL
#
# JSONL = one valid JSON object per line.
# ==================================================

with open(
    OUTPUT_DATASET_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        json.dumps(
            evaluation_record,
            ensure_ascii=False
        )
    )

    file.write(
        "\n"
    )


# ==================================================
# 7. Console output
# ==================================================

print(
    "\nFoundry evaluation dataset created."
)

print(
    f"\nCase count: 1"
)

print(
    f"\nDataset:"
    f"\n{OUTPUT_DATASET_FILE}"
)

print(
    "\nFields:"
    "\n- query"
    "\n- context"
    "\n- response"
    "\n- case_id"
    "\n- model"
    "\n- contract_version"
    "\n- prompt_version"
)

print(
    "\nNo real company data was used."
)