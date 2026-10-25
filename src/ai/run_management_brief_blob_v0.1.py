from pathlib import Path
from datetime import datetime, timezone
import argparse
import subprocess
import sys

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


# ==================================================
# Project
# ==================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

PIPELINE_FILE = (
    PROJECT_ROOT
    / "src"
    / "ai"
    / "run_management_brief_pipeline_v0.1.py"
)


# ==================================================
# Arguments
# ==================================================

parser = argparse.ArgumentParser(
    description=(
        "Run the governed Management Brief pipeline "
        "using Azure Blob Storage input/output."
    )
)

parser.add_argument(
    "--storage-account",
    required=True,
)

parser.add_argument(
    "--input-container",
    required=True,
)

parser.add_argument(
    "--input-blob",
    required=True,
)

parser.add_argument(
    "--output-container",
    required=True,
)

args = parser.parse_args()


# ==================================================
# Runtime folders
# ==================================================

run_id = datetime.now(
    timezone.utc
).strftime(
    "%Y%m%dT%H%M%SZ"
)


runtime_root = (
    Path("/tmp/governed-ai-commerce/blob_run")
    / run_id
)

input_folder = (
    runtime_root
    / "input"
)

output_folder = (
    runtime_root
    / "output"
)


input_folder.mkdir(
    parents=True,
    exist_ok=True,
)

output_folder.mkdir(
    parents=True,
    exist_ok=True,
)


context_file = (
    input_folder
    / "management_brief_context.json"
)


# ==================================================
# Azure Storage connection
# ==================================================

account_url = (
    f"https://{args.storage_account}"
    ".blob.core.windows.net"
)


credential = DefaultAzureCredential()


blob_service_client = BlobServiceClient(
    account_url=account_url,
    credential=credential,
)


# ==================================================
# Download trusted context
# ==================================================

print(
    "\nDownloading trusted aggregated context..."
)


input_blob_client = (
    blob_service_client
    .get_blob_client(
        container=args.input_container,
        blob=args.input_blob,
    )
)


context_bytes = (
    input_blob_client
    .download_blob()
    .readall()
)


context_file.write_bytes(
    context_bytes
)


print(
    "Trusted context download: PASS"
)


# ==================================================
# Run existing governed pipeline
# ==================================================

pipeline_command = [

    sys.executable,

    str(
        PIPELINE_FILE
    ),

    "--context",
    str(
        context_file
    ),

    "--output-root",
    str(
        output_folder
    ),

    "--data-classification",
    "PRIVATE_AGGREGATED",
]


pipeline_result = subprocess.run(
    pipeline_command
)


# ==================================================
# Upload generated artifacts
# ==================================================

uploaded_files = 0


if output_folder.exists():

    for local_file in (
        output_folder.rglob("*")
    ):

        if not local_file.is_file():

            continue

        relative_path = (
            local_file
            .relative_to(
                output_folder
            )
            .as_posix()
        )

        output_blob_name = (
            f"{run_id}/"
            f"{relative_path}"
        )


        output_blob_client = (
            blob_service_client
            .get_blob_client(
                container=args.output_container,
                blob=output_blob_name,
            )
        )


        output_blob_client.upload_blob(
            local_file.read_bytes(),
            overwrite=True,
        )


        uploaded_files += 1


print(
    f"\nUploaded output artifacts: "
    f"{uploaded_files}"
)


# ==================================================
# Final status
# ==================================================

if pipeline_result.returncode == 0:

    print(
        "\nBLOB GOVERNED AI RUN: PASS"
    )

else:

    print(
        "\nBLOB GOVERNED AI RUN: BLOCKED"
    )


sys.exit(
    pipeline_result.returncode
)
