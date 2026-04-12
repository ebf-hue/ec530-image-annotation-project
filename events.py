import uuid
from datetime import datetime, timezone

# base event to avoid repeating too much
def _base_event(topic: str, payload: dict) -> dict:
    return {
        "type": "publish",
        "topic": topic,
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

def image_submitted(image_id: str, path: str, source: str) -> dict:
    return _base_event("image.submitted", {
        "image_id": image_id,
        "path": path,
        "source": source,
    })

def inference_completed(image_id: str, objects: list) -> dict:
    return _base_event("inference.completed", {
        "image_id": image_id,
        "objects": objects,  # list of {label, bbox, conf}
    })

def annotation_stored(image_id: str, doc_id: str) -> dict:
    return _base_event("annotation.stored", {
        "image_id": image_id,
        "doc_id": doc_id,
    })

def embedding_created(image_id: str, vector: list) -> dict:
    return _base_event("embedding.created", {
        "image_id": image_id,
        "vector": vector,
    })

def annotation_corrected(image_id: str, correction: dict) -> dict:
    return _base_event("annotation.corrected", {
        "image_id": image_id,
        "correction": correction,  # {label_old, label_new}
    })

def query_submitted(query_text: str, top_k: int = 4) -> dict:
    return _base_event("query.submitted", {
        "query_text": query_text,
        "top_k": top_k,
    })

def query_completed(query_text: str, results: list) -> dict:
    return _base_event("query.completed", {
        "query_text": query_text,
        "results": results,  # list of {image_id, score}
    })

# validate requireed fields
REQUIRED_FIELDS = {"type", "topic", "event_id", "timestamp", "payload"}

def validate_event(event: dict) -> bool:
    return REQUIRED_FIELDS.issubset(event.keys())

