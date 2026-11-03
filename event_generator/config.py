from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GeneratorConfig:
    users: int = 1_000
    sessions_per_user_min: int = 1
    sessions_per_user_max: int = 3
    start_date: str = "2025-01-01"
    end_date: str = "2025-01-31"
    seed: int = 42
    output: Path = Path("data/synthetic/events/events.jsonl")
    products_csv: Path = Path("data/raw/products.csv")
