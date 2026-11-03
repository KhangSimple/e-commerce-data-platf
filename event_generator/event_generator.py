import random
import uuid
from datetime import datetime, timedelta, timezone
from .models import Event
from .user_simulator import UserSimulator

DEVICES = ["desktop", "mobile", "tablet"]

class EventGenerator:
    def __init__(self, products, *, seed=42, start_date="2025-01-01", end_date="2025-01-31"):
        if not products:
            raise ValueError("products must not be empty")
        self.products = list(products)
        self.rng = random.Random(seed)
        self.simulator = UserSimulator(self.rng)
        self.start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
        self.end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
        if self.end < self.start:
            raise ValueError("end_date must be >= start_date")

    def _random_session_start(self):
        seconds = int((self.end - self.start).total_seconds())
        return self.start + timedelta(seconds=self.rng.randint(0, max(0, seconds)))

    def generate_session(self, user_id):
        session_id = str(uuid.uuid4())
        journey = self.simulator.generate_journey()
        device = self.rng.choice(DEVICES)
        timestamp = self._random_session_start()
        events = []
        # Keep the selected product stable for cart/checkout/purchase in this V1.
        product_id = self.rng.choice(self.products)
        synthetic_order_id = str(uuid.uuid4()) if "purchase" in journey else None
        purchase_price = round(self.rng.uniform(10, 500), 2) if synthetic_order_id else None

        for event_type in journey:
            timestamp += timedelta(seconds=self.rng.randint(2, 90))
            events.append(Event.create(
                event_type=event_type,
                timestamp=timestamp,
                user_id=user_id,
                session_id=session_id,
                product_id=product_id,
                device=device,
                order_id=synthetic_order_id if event_type == "purchase" else None,
                price=purchase_price if event_type == "purchase" else None,
            ))
        return events
