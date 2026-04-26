# Subscribes to: inference.completed
# Publishes: annotation.stored

from pymongo import MongoClient
from events import annotation_stored

client = MongoClient("mongodb://localhost:27017/")
db = client["image_annotation_db"]
annotations_collection = db["annotations"]


def _build_annotation_doc(event: dict) -> dict:
    payload = event["payload"]

    return {
        "_id": payload["image_id"],
        "image_id": payload["image_id"],
        "path": payload["path"],
        "objects": payload["objects"],
        "review": {
            "status": "uncorrected",
            "notes": [],
        }
    }


def handle_inference_completed(event, broker):
    # simulate creating document + storing in document DB
    payload = event["payload"]
    image_id = payload["image_id"]
    doc_id = f"doc_{image_id}"

    # create document to store
    doc = _build_annotation_doc(event)

    # insert to mongodb annotations table we made earlier
    annotations_collection.replace_one(
        {"_id": image_id},
        doc,
        upsert=True,
    )

    # publish the embedding created event
    stored_event = annotation_stored(
        image_id=image_id,
        doc_id=doc_id,
        path=payload["path"],
    )
    print(f"[Document_DB] Stored annotation document for image with image_id={image_id}")
    return broker.publish(stored_event)


def get_document(image_id: str):
    return annotations_collection.find_one({"_id": image_id})