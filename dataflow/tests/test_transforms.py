import json
from datetime import datetime, timezone

from pipeline.transforms import (
    parse_json_message,
    normalize_event,
    ParseAndValidateEvent,
)


def valid_event():
    return {
        "event_id": "3be19afd-9083-459a-b52c-91047dc233f7",
        "event_type": "view_product",
        "event_version": 1,
        "event_timestamp": "2025-01-02T10:45:28+00:00",
        "user_id": "9a391277128ca32d4ef8473910faf70a",
        "session_id": "16da26bc-87b9-4460-987c-6b51117528b0",
        "product_id": "8f03c5b78e41d6cecdfb6f6bbe4de8da",
        "device": "desktop",
        "source": "web",
        "order_id": None,
        "price": None,
        "data_origin": "synthetic",
    }


# --------------------------------------------------
# Test parse_json_message
# --------------------------------------------------


def test_parse_json_message():
    event = valid_event()
    message = json.dumps(event).encode("utf-8")

    result = parse_json_message(message)

    assert result == event
    assert isinstance(result, dict)


# --------------------------------------------------
# Test normalize_event
# --------------------------------------------------


def test_normalize_event():
    event = valid_event()

    result = normalize_event(event)

    assert result["event_id"] == "3be19afd-9083-459a-b52c-91047dc233f7"
    assert result["event_type"] == "view_product"
    assert result["user_id"] == "9a391277128ca32d4ef8473910faf70a"
    assert result["session_id"] == "16da26bc-87b9-4460-987c-6b51117528b0"
    assert result["product_id"] == "8f03c5b78e41d6cecdfb6f6bbe4de8da"

    # # Verify event_timestamp
    # expected_timestamp = datetime.fromtimestamp(
    #     event["event_timestamp"].replace("Z", "+00:00")
    # )

    # assert result["event_timestamp"] == expected_timestamp

    # Verify ingestion_timestamp is valid ISO format
    # ingestion_timestamp = result["ingestion_timestamp"]

    # assert ingestion_timestamp.tzinfo is not None

    # Verify output schema
    assert result["is_valid"] is True
    assert result["error_message"] is None
    assert result["order_id"] is None
    assert result["price"] is None


# --------------------------------------------------
# Test ParseAndValidateEvent DoFn
# --------------------------------------------------


def test_parse_and_validate_event_valid():
    event = valid_event()
    message = json.dumps(event).encode("utf-8")

    result = list(ParseAndValidateEvent().process(message))

    assert len(result) == 1
    assert result[0]["event_id"] == "3be19afd-9083-459a-b52c-91047dc233f7"
    assert result[0]["is_valid"] is True


def test_parse_and_validate_event_invalid():
    event = valid_event()

    # Missing required field
    event.pop("event_id")

    message = json.dumps(event).encode("utf-8")

    result = list(ParseAndValidateEvent().process(message))

    assert result == []


def test_parse_and_validate_event_invalid_json():
    message = b"{invalid json"

    result = list(ParseAndValidateEvent().process(message))

    assert result == []
