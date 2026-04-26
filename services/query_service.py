# Subscribes to: query_submitted
# Publishes: query_completed

from events import query_completed
from services.vector_db_service import vectors_collection


def handle_query_submitted(event, broker):
    payload = event["payload"]
    query_text = payload["query_text"]
    top_k = payload["top_k"]

    #Always returns the top k regardless of query for mocking purposes
    results = list(vectors_collection.find().limit(top_k))

    image_ids = [r["_id"] for r in results]

    print(f"[QueryService] Found results for '{query_text}': {image_ids}")

    completed_event = query_completed(
        query_text=query_text,
        results=image_ids
    )

    return broker.publish(completed_event)