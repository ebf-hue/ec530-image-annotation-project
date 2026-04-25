import pytest
from unittest.mock import MagicMock
from broker import Broker
from events import image_submitted

class TestErrorFields:
    @pytest.mark.parametrize(
        "event",
        [
            {"type": "Uma Musume"},
            {"type": "publish", "topic": "Mejiro Palmer"},
            {"type": "publish", "topic": "query.completed", "timestamp": "Daitaku Helios"},
            {'type': 'publish', 'topic': 'image.submitted', 'event_id': 'Daiichi Ruby', 'payload': {'image_id': 'img_001', 'path': 'images/street.jpg', 'source': 'camera_A'}}
        ]
    )
    def test_return_broker_rejects_malformed_event(self, event):
        broker = Broker()
        broker.client = MagicMock()
        broker.publish(event)
        broker.client.publish.assert_not_called()

class TestBrokerProperFunctionality:
    def test_successful_redis_call(self):
        broker = Broker()
        broker.client = MagicMock()
        event = image_submitted("img_001", "images/street.jpg")
        broker.publish(event)
        broker.client.publish.assert_called_once()

    def test_successful_registers_topic(self):
        broker = Broker()
        broker.pubsub = MagicMock()
        handler = MagicMock()
        broker.subscribe("image.submitted", handler)
        broker.pubsub.subscribe.assert_called_once()
