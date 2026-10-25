import re
from pathlib import Path
from typing import Any


# ==================================================
# Direct identifiers forbidden from AI context
# ==================================================

FORBIDDEN_KEYS = {
    "customer_name",
    "customer_first_name",
    "customer_last_name",
    "first_name",
    "last_name",

    "email",
    "email_address",

    "phone",
    "phone_number",
    "telephone",
    "mobile",
    "mobile_number",

    "address",
    "customer_address",
    "shipping_address",
    "billing_address",
    "street",
    "street_name",
    "house_number",

    "customer_id",
    "customer_number",
    "kunden_nr",
    "kundennr",

    "order_id",
    "order_number",
    "order_no",
    "order_line_id",

    "shipment_id",

    "tracking_number",
    "tracking_no",
    "tracking_id",

    "postal_code",
    "zip_code",
    "plz",
}


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+"
    r"\.[A-Za-z]{2,}\b"
)


def normalize_key(
    key: str,
) -> str:

    return re.sub(
        r"[^a-z0-9]+",
        "_",
        key.lower(),
    ).strip("_")


def scan_context(
    value: Any,
    path: str = "$",
) -> list[dict]:

    violations = []

    if isinstance(
        value,
        dict,
    ):

        for key, child in value.items():

            normalized_key = normalize_key(
                str(key)
            )

            child_path = (
                f"{path}.{key}"
            )

            if normalized_key in FORBIDDEN_KEYS:

                violations.append(
                    {
                        "type":
                            "FORBIDDEN_KEY",

                        "path":
                            child_path,

                        "key":
                            str(key),
                    }
                )

            violations.extend(
                scan_context(
                    child,
                    child_path,
                )
            )

    elif isinstance(
        value,
        list,
    ):

        for index, child in enumerate(
            value
        ):

            violations.extend(
                scan_context(
                    child,
                    f"{path}[{index}]",
                )
            )

    elif isinstance(
        value,
        str,
    ):

        if EMAIL_PATTERN.search(
            value
        ):

            violations.append(
                {
                    "type":
                        "EMAIL_LIKE_VALUE",

                    "path":
                        path,
                }
            )

    return violations


def validate_cloud_context(
    context: Any,
) -> list[dict]:

    return scan_context(
        context
    )


def path_is_inside(
    child: Path,
    parent: Path,
) -> bool:

    child = child.resolve()
    parent = parent.resolve()

    try:

        child.relative_to(
            parent
        )

        return True

    except ValueError:

        return False