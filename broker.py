# broker.py

import json
import redis
from events import validate_event
import logging

logger = logging.getLogger(__name__)

# broker will act as the middleman between the events.py schemas and the actual Redis data
class Broker:
    def __init__(self):
        # to pub, localhost on port 5678
        
        self.client = redis.Redis(host = "localhost", port = 5678, decode_responses=True)
        # to sub
        self.pubsub = self.client.pubsub()

    def publish(self, event: dict):
        # validate event
        if not validate_event(event):
            logger.warning("Oops, rejected malformed event: %s", event)
            return False
        topic = event["topic"]
        # json.dumps converts to json string
        self.client.publish(topic, json.dumps(event))
        return True

    # subscribe
    def subscribe(self, topic: str, handler):
        self.pubsub.subscribe(**{topic: lambda msg: self._handle(msg, handler)})

    # handle a msg
    def _handle(self, msg, handler):
        try:
            event = json.loads(msg["data"])
            handler(event)
        except Exception as e:
            print(f"[oops] error handling msg: {e}")

    # listen
    def listen(self):
        for _ in self.pubsub.listen():
            pass
        
