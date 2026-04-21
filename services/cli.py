# Publishes: image.submitted, query.submitted
# Entry point for user interaction

from services.upload_service import handle_cli_image
from events import query_submitted

def simulate_upload(broker):
    image_id = input("Image ID: ").strip()
    path = input("Image path: ").strip()

    ok = handle_cli_image(broker, image_id=image_id, path=path)
    if ok:
        print(f"Submitted image {image_id}")
    else:
        print(f"Oops, could not submit image {image_id}")

def simulate_query(broker):
    query_text = input("Query text: ").strip()
    top_k_text = input("Top k (default 4): ").strip()
    top_k = int(top_k_text) if top_k_text else 4

    event = query_submitted(query_text=query_text, top_k=top_k)
    ok = broker.publish(event)

    if ok:
        print(f"Submitted query '{query_text}'")
    else:
        print(f"Oops could not submit query")