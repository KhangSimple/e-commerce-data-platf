from datetime import datetime

ALLOWED_EVENTS = {
    "view_product",
    "add_to_cart",
    "remove_from_cart",
    "begin_checkout",
    "purchase",
}


def validate_session(events):
    errors = []
    warning = []
    if not events:
        return ["empty session"]
    session_ids = {e.session_id for e in events}
    users = {e.user_id for e in events}
    event_ids = {e.event_id for e in events}
    if len(set(event_ids)) != len(events):
        warning.append("duplicate event_id within session")
    if len(session_ids) != 1:
        errors.append("session_id differs within session")
    if len(users) != 1:
        errors.append("user_id differs within session")

    times = [datetime.fromisoformat(e.event_timestamp) for e in events]
    if times != sorted(times):
        errors.append("timestamps are not ordered")

    types = [e.event_type for e in events]
    if any(t not in ALLOWED_EVENTS for t in types):
        errors.append("unknown event_type")
    if "purchase" in types:
        purchase = next(e for e in events if e.event_type == "purchase")
        if not purchase.order_id or purchase.price is None:
            errors.append("purchase must have order_id and price")
    return errors, warning
