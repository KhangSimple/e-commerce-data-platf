import random
import copy
from datetime import timedelta


class FaultInjector:
    def __init__(
        self,
        duplicate_rate=0.01,
        late_rate=0.005,
        min_delay_seconds=60,
        max_delay_seconds=300,
        invalid_rate=0.01,
        seed=42,
    ):
        self.rng = random.Random(seed)
        self.duplicate_rate = duplicate_rate
        self.late_rate = late_rate
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.invalid_rate = invalid_rate

    def inject(self, event):
        """Return event copies with injected faults."""
        output = [copy.deepcopy(event)]

        # 1. Duplicate
        if self.rng.random() < self.duplicate_rate:
            output.append(copy.deepcopy(event))

        # 2. Backdated event
        if self.rng.random() < self.late_rate:
            late_event = copy.deepcopy(event)

            late_event["event_timestamp"] -= timedelta(
                seconds=self.rng.randint(self.min_delay_seconds, self.max_delay_seconds)
            )
            output.append(late_event)

        # 3. Invalid event
        if self.rng.random() < self.invalid_rate:
            invalid_event = copy.deepcopy(event)
            invalid_event["event_type"] = "invalid_event"
            invalid_event["price"] = -100
            output.append(invalid_event)

        return output
