from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Event:
    event_id: str
    event_type: str
    event_version: int
    event_timestamp: str
    user_id: str
    session_id: str
    product_id: str
    device: str
    source: str = "web"
    order_id: Optional[str] = None
    price: Optional[float] = None
    data_origin: str = "synthetic"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def create(cls, *, event_type, timestamp: datetime, user_id, session_id,
               product_id, device, order_id=None, price=None):
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            event_version=1,
            event_timestamp=timestamp.isoformat(),
            user_id=user_id,
            session_id=session_id,
            product_id=product_id,
            device=device,
            order_id=order_id,
            price=price,
        )
