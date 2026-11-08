from pipeline.validation import validate_event


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


def test_valid_event():
    is_valid, error = validate_event(valid_event())

    assert is_valid is True
    assert error == ""


def test_missing_event_id():
    event = valid_event()
    event.pop("event_id")

    is_valid, error = validate_event(event)

    assert is_valid is False
    assert "Missing fields" in error


def test_invalid_event_type():
    event = valid_event()
    event["event_type"] = "invalid_event"

    is_valid, error = validate_event(event)

    assert is_valid is False
    assert "Unsupported" in error


def test_purchase_without_order_id():
    event = valid_event()
    event["event_type"] = "purchase"

    is_valid, error = validate_event(event)

    assert is_valid is False
    assert "order_id" in error


def test_purchase_negative_price():
    event = valid_event()
    event["event_type"] = "purchase"
    event["order_id"] = "SYN_ORDER_001"
    event["price"] = -100

    is_valid, error = validate_event(event)

    assert is_valid is False
    assert "negative" in error
