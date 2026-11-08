# pipeline/main.py

import argparse

import apache_beam as beam

from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    StandardOptions,
)

from pipeline.transforms import ParseAndValidateEvent


def run(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--subscription",
        required=True,
    )

    parser.add_argument(
        "--output_table",
        required=True,
    )

    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)

    standard_options = pipeline_options.view_as(StandardOptions)
    standard_options.streaming = True

    with beam.Pipeline(options=pipeline_options) as pipeline:

        events = pipeline | "ReadFromPubSub" >> ReadFromPubSub(
            subscription=known_args.subscription
        )

        valid_events = events | "ParseValidateNormalize" >> beam.ParDo(
            ParseAndValidateEvent()
        )

        _ = valid_events | "WriteToBigQuery" >> WriteToBigQuery(
            table=known_args.output_table,
            schema={
                "fields": [
                    {"name": "event_id", "type": "STRING"},
                    {"name": "event_type", "type": "STRING"},
                    {"name": "event_timestamp", "type": "TIMESTAMP"},
                    {"name": "ingestion_timestamp", "type": "TIMESTAMP"},
                    {"name": "user_id", "type": "STRING"},
                    {"name": "session_id", "type": "STRING"},
                    {"name": "product_id", "type": "STRING"},
                    {"name": "device", "type": "STRING"},
                    {"name": "source", "type": "STRING"},
                    {"name": "order_id", "type": "STRING"},
                    {"name": "price", "type": "FLOAT"},
                    {"name": "data_origin", "type": "STRING"},
                    {"name": "is_valid", "type": "BOOLEAN"},
                    {"name": "error_message", "type": "STRING"},
                ]
            },
            create_disposition=(beam.io.BigQueryDisposition.CREATE_NEVER),
            write_disposition=(beam.io.BigQueryDisposition.WRITE_APPEND),
            method=WriteToBigQuery.Method.STORAGE_WRITE_API,
        )


if __name__ == "__main__":
    run()
