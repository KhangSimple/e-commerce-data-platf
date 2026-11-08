import argparse
import csv
import json
from pathlib import Path
from collections import Counter
from .config import GeneratorConfig
from .event_generator import EventGenerator
from .publisher import PubSubPublisher
from .validation import validate_session


def load_products(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        # Olist product identifier column is product_id.
        return [row["product_id"] for row in reader if row.get("product_id")]


def load_customers(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        # Olist customer identifier column is customer_id.
        return [row["customer_id"] for row in reader if row.get("customer_id")]


def run(config: GeneratorConfig):
    products = load_products(config.products_csv)
    customers = load_customers(config.customers_csv)
    generator = EventGenerator(
        users=customers,
        products=products,
        seed=config.seed,
        start_date=config.start_date,
        end_date=config.end_date,
    )
    publisher = (
        PubSubPublisher(config.project_id, config.topic)
        if config.mode == "pubsub"
        else None
    )
    config.output.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    total = 0
    with config.output.open("w", encoding="utf-8") as f:
        for customer_id in generator.rng.choices(customers, k=config.users):
            user_id = customer_id
            for _ in range(
                generator.rng.randint(
                    config.sessions_per_user_min, config.sessions_per_user_max
                )
            ):
                session = generator.generate_session(user_id)
                errors, warning = validate_session(session)
                if errors:
                    raise RuntimeError(f"Invalid session: {errors}")
                for event in session:
                    f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
                    if config.mode == "pubsub":
                        publisher.publish(event.to_dict())

                    counts[event.event_type] += 1
                    total += 1
        if warning:
            print("Warnings during validation:", set(warning))
    print(f"Wrote {total:,} events to {config.output}")
    print("Event counts:", dict(counts))


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic ecommerce events")
    parser.add_argument("--users", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--start-date", default="2025-01-01")
    parser.add_argument("--end-date", default="2025-01-31")
    parser.add_argument("--duplicate-rate", type=float, default=0.01)
    parser.add_argument("--invalid-rate", type=float, default=0.01)
    parser.add_argument("--late-rate", type=float, default=0.005)
    parser.add_argument("--min-delay-seconds", type=int, default=60)
    parser.add_argument("--max-delay-seconds", type=int, default=300)
    parser.add_argument("--products-csv", default="data/raw/products.csv")
    parser.add_argument("--customers-csv", default="data/raw/customers.csv")
    parser.add_argument("--output", default="data/synthetic/events/events.jsonl")

    parser.add_argument("--mode", default="file")
    parser.add_argument("--project-id", default="klostctrl-portfolio")
    parser.add_argument("--topic", default="ecommerce-events")
    parser.add_argument("--eps", type=int, default=1000)

    args = parser.parse_args()
    config = GeneratorConfig(
        users=args.users,
        seed=args.seed,
        start_date=args.start_date,
        end_date=args.end_date,
        duplicate_rate=args.duplicate_rate,
        invalid_rate=args.invalid_rate,
        late_rate=args.late_rate,
        min_delay_seconds=args.min_delay_seconds,
        max_delay_seconds=args.max_delay_seconds,
        products_csv=Path(args.products_csv),
        customers_csv=Path(args.customers_csv),
        output=Path(args.output),
        mode=args.mode,
        project_id=args.project_id,
        topic=args.topic,
        eps=args.eps,
    )
    run(config)


if __name__ == "__main__":
    main()
