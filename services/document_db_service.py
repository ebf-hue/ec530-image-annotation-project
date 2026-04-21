# Subscribes to: inference.completed
# Publishes: annotation.stored

from datetime import datetime, timezone
from events import annotation_stored

DOCUMENT_DB = {}

def _build_annotation_doc(event: dict) -> dict:
    payload = event["payload"]
    image_id = payload["image_id"]
    objects = payload["objects"]

    return {
        "image_id": image_id,
        "objects": objects,
        "review": {
            "status": "uncorrected",
            "notes": [],
        },
    }

def handle_inference_completed(event, broker):
    payload = event["payload"]
    image_id = payload["image_id"]

    # idempotency: do not create duplicate document state
    if image_id in DOCUMENT_DB:
        doc_id = f"doc_{image_id}"
        stored_event = annotation_stored(image_id=image_id, doc_id=doc_id)
        return broker.publish(stored_event)

    doc = _build_annotation_doc(event)
    DOCUMENT_DB[image_id] = doc

    doc_id = f"doc_{image_id}"
    stored_event = annotation_stored(image_id=image_id, doc_id=doc_id)
    return broker.publish(stored_event)

def get_document(image_id: str):
    return DOCUMENT_DB.get(image_id)