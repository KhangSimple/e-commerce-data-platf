import json
import logging
from datetime import datetime, timezone
from apache_beam.utils.timestamp import Timestamp

import apache_beam as beam

from pipeline.validation import validate_event


def parse_json_message(message: bytes) -> dict:
    """Decode Pub/Sub bytes and parse JSON."""
    return json.loads(message.decode("utf-8"))


def normalize_event(event: dict) -> dict:
    """Convert source event into BigQuery-compatible row."""

    event_timestamp = Timestamp.from_utc_datetime(
        datetime.fromisoformat(
            event["event_timestamp"].replace("Z", "+00:00")
        ).astimezone(timezone.utc)
    )

    ingestion_timestamp = Timestamp.now()

    return {
        "event_id": event["event_id"],
        "event_type": event["event_type"],
        "event_timestamp": event_timestamp,
        "ingestion_timestamp": ingestion_timestamp,
        "user_id": event["user_id"],
        "session_id": event["session_id"],
        "product_id": event.get("product_id"),
        "device": event.get("device"),
        "source": event.get("source"),
        "order_id": event.get("order_id"),
        "price": event.get("price"),
        "data_origin": event.get("data_origin"),
        "is_valid": True,
        "error_message": None,
    }


class ParseAndValidateEvent(beam.DoFn):
    """Parse, validate and normalize Pub/Sub event."""

    def process(self, message: bytes):
        try:
            event = parse_json_message(message)

            is_valid, error_message = validate_event(event)

            if not is_valid:
                logging.warning(
                    "Invalid event: %s",
                    error_message,
                )
                return

            yield normalize_event(event)

        except Exception as exc:
            logging.exception(
                "Failed to process Pub/Sub message: %s",
                exc,
            )
