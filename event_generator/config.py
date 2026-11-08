from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GeneratorConfig:
    users: int = 1000
    sessions_per_user_min: int = 1
    sessions_per_user_max: int = 3
    start_date: str = "2025-01-01"
    end_date: str = "2025-01-31"
    seed: int = 42
    duplicate_rate: float = 0.01
    invalid_rate: float = 0.01
    late_rate: float = 0.005
    min_delay_seconds: int = 60
    max_delay_seconds: int = 300
    output: Path = Path("data/synthetic/events/events.jsonl")
    products_csv: Path = Path("data/raw/products.csv")
    customers_csv: Path = Path("data/raw/customers.csv")

    mode: str = "file"
    project_id: str = "klostctrl-portfolio"
    topic: str = "ecommerce-events"
    eps: int = 1000
