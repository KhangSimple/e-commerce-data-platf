import json
from google.cloud import pubsub_v1


class PubSubPublisher:
    def __init__(self, project_id, topic_id):
        self.publisher = pubsub_v1.PublisherClient()

        self.topic_path = self.publisher.topic_path(project_id, topic_id)

    def publish(self, event):
        payload = json.dumps(event).encode("utf-8")

        future = self.publisher.publish(
            self.topic_path,
            payload,
            event_type=event["event_type"],
            event_id=event["event_id"],
        )

        return future.result()
