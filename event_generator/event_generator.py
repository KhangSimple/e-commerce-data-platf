import random
import uuid
from datetime import datetime, timedelta, timezone
from .models import Event
from .user_simulator import UserSimulator
from .fault_injector import FaultInjector

DEVICES = ["desktop", "mobile", "tablet"]


class EventGenerator:
    def __init__(
        self,
        users,
        products,
        *,
        seed=42,
        start_date="2025-01-01",
        end_date="2025-01-31",
        duplicate_rate=0.01,
        late_rate=0.005,
        min_delay_seconds=60,
        max_delay_seconds=300,
        invalid_rate=0.01,
    ):
        if not products:
            raise ValueError("products must not be empty")
        self.users = list(users)
        self.products = list(products)
        self.rng = random.Random(seed)
        self.simulator = UserSimulator(self.rng)
        self.start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
        self.end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
        self.duplicate_rate = duplicate_rate
        self.late_rate = late_rate
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.invalid_rate = invalid_rate
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
        purchase_price = (
            round(self.rng.uniform(10, 500), 2) if synthetic_order_id else None
        )

        fault_injector = FaultInjector(
            duplicate_rate=self.duplicate_rate,
            late_rate=self.late_rate,
            invalid_rate=self.invalid_rate,
            min_delay_seconds=self.min_delay_seconds,
            max_delay_seconds=self.max_delay_seconds,
        )

        for event_type in journey:
            timestamp += timedelta(seconds=self.rng.randint(2, 90))
            event = Event.create(
                event_type=event_type,
                timestamp=timestamp,
                user_id=user_id,
                session_id=session_id,
                product_id=product_id,
                device=device,
                order_id=synthetic_order_id if event_type == "purchase" else None,
                price=purchase_price if event_type == "purchase" else None,
            )
            events.extend(fault_injector.inject(event))

        return events
