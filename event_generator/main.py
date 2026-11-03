import argparse
import csv
import json
from pathlib import Path
from collections import Counter
from .config import GeneratorConfig
from .event_generator import EventGenerator
from .validation import validate_session


def load_products(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        # Olist product identifier column is product_id.
        return [row["product_id"] for row in reader if row.get("product_id")]


def run(config: GeneratorConfig):
    products = load_products(config.products_csv)
    generator = EventGenerator(
        products,
        seed=config.seed,
        start_date=config.start_date,
        end_date=config.end_date,
    )
    config.output.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    total = 0
    with config.output.open("w", encoding="utf-8") as f:
        for i in range(config.users):
            user_id = f"synthetic_user_{i:06d}"
            for _ in range(
                generator.rng.randint(
                    config.sessions_per_user_min, config.sessions_per_user_max
                )
            ):
                session = generator.generate_session(user_id)
                errors = validate_session(session)
                if errors:
                    raise RuntimeError(f"Invalid session: {errors}")
                for event in session:
                    f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
                    counts[event.event_type] += 1
                    total += 1
    print(f"Wrote {total:,} events to {config.output}")
    print("Event counts:", dict(counts))


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic ecommerce events")
    parser.add_argument("--users", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--start-date", default="2025-01-01")
    parser.add_argument("--end-date", default="2025-01-31")
    parser.add_argument("--products-csv", default="data/raw/products.csv")
    parser.add_argument("--output", default="data/synthetic/events/events.jsonl")
    args = parser.parse_args()
    config = GeneratorConfig(
        users=args.users,
        seed=args.seed,
        start_date=args.start_date,
        end_date=args.end_date,
        products_csv=Path(args.products_csv),
        output=Path(args.output),
    )
    run(config)


if __name__ == "__main__":
    main()
