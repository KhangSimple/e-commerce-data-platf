from datetime import datetime, timezone
from typing import Any

REQUIRED_FIELDS = [
    "event_id",
    "event_type",
    "event_timestamp",
    "user_id",
    "session_id",
    "product_id",
    "device",
    "source",
]

ALLOWED_EVENT_TYPES = {
    "view_product",
    "add_to_cart",
    "remove_from_cart",
    "begin_checkout",
    "purchase",
}


def validate_event(event: dict[str, Any]) -> tuple[bool, str]:
    """Validate event schema and basic business rules."""

    missing_fields = [field for field in REQUIRED_FIELDS if event.get(field) is None]

    if missing_fields:
        return False, f"Missing fields: {missing_fields}"

    if event["event_type"] not in ALLOWED_EVENT_TYPES:
        return False, "Unsupported event_type"

    # if not isinstance(event["event_timestamp"], (int, float)):
    #     return False, "event_timestamp must be Unix timestamp"

    try:
        datetime.fromisoformat(event["event_timestamp"])
    except (ValueError, OverflowError, OSError):
        return False, "Invalid event_timestamp"

    if event["event_type"] == "purchase":
        if not event.get("order_id"):
            return False, "Purchase requires order_id"

        price = event.get("price")

        if not isinstance(price, (int, float)):
            return False, "Purchase requires numeric price"

        if price < 0:
            return False, "Purchase price cannot be negative"

    return True, ""
