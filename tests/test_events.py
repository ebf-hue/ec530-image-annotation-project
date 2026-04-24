import pytest
from events import (
    image_submitted, inference_completed, annotation_stored,
    embedding_created, annotation_corrected, query_submitted,
    query_completed, validate_event
)


class TestEventValidation:

    @pytest.mark.parametrize(
        "event",
        [
            {"type": "publish", "event_id": "evt_001", "timestamp": "2026-04-12", "payload": {}},
            {"type": "publish", "topic": "image.submitted", "event_id": "evt_001", "timestamp": "2026-04-12"}
        ]
    )
    def test_return_false_if_missing_fields(self,event):
        assert not validate_event(event)

    @pytest.mark.parametrize(
        "event",
        [
            image_submitted("img_001", "images/street.jpg"),
            inference_completed("img_001", [{"label": "car", "bbox": [0,0,100,100], "conf": 0.9}]),
            annotation_stored("img_001", "doc_001"),
            embedding_created("img_001", [0.1, 0.2, 0.3]),
            annotation_corrected("img_001", {"label_old": "car", "label_new": "truck"}),
            query_submitted("find cars"),
            query_completed("find cars", [{"image_id": "img_001", "score": 0.95}]),
        ]
    )
    def test_return_true_valid_events(self,event):
        assert validate_event(event)

class TestPayload:
    def test_image_submitted_payload(self):
        event = image_submitted("img_001", "images/street.jpg")
        assert event["payload"]["image_id"] == "img_001"
        assert event["payload"]["path"] == "images/street.jpg"
        assert event["topic"] == "image.submitted"

    def test_inference_completed_payload(self):
        objects = [{"label": "car", "bbox": [0,0,100,100], "conf": 0.9}]
        event = inference_completed("img_001", objects, "images/car.jpg")
        assert event["topic"] == "inference.completed"
        assert event["payload"]["objects"] == objects

    def test_annotation_stored_payload(self):
        event = annotation_stored("img_001", "doc_001", "images/a.jpg")
        assert event["topic"] == "annotation.stored"
        assert event["payload"]["doc_id"] == "doc_001"
    
    def test_embedding_created_payload(self):
        event = embedding_created("img_001", [0.1, 0.2, 0.3])
        assert event["topic"] == "embedding.created"
        assert event["payload"]["vector"] == [0.1, 0.2, 0.3]
    
    def test_query_submitted_default_top_k(self):
        event = query_submitted("find cars")
        assert event["payload"]["top_k"] == 4
    
    def test_each_event_has_unique_event_id(self):
        e1 = image_submitted("img_001", "images/a.jpg")
        e2 = image_submitted("img_001", "images/a.jpg")
        assert e1["event_id"] != e2["event_id"]

    def test_annotation_corrected_payload(self):
        correction = {"label_old": "car", "label_new": "truck"}
        event = annotation_corrected("img_001", correction)
        assert event["topic"] == "annotation.corrected"
        assert event["payload"]["correction"] == correction
    
    def test_query_completed_payload(self):
        results = [{"image_id": "img_001", "score": 0.95}]
        event = query_completed("find cars", results)
        assert event["topic"] == "query.completed"
        assert event["payload"]["results"] == results
