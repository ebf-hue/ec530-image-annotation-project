# Subscribes to: image.submitted
# Publishes: inference.completed

from events import inference_completed

def _fake_detect_objects(image_path: str) -> list[dict]:
    # Fake simulated data for now
    if "street" in image_path.lower():
        return [
            {"label": "car", "bbox": [12, 44, 188, 200], "conf": 0.93},
            {"label": "person", "bbox": [230, 51, 286, 210], "conf": 0.88},
        ]
    if "horse" in image_path.lower():
        return [
            {"label": "horse", "bbox": [30, 40, 150, 180], "conf": 0.96}
        ]
    return [
        {"label": "unknown_object", "bbox": [0, 0, 100, 100], "conf": 0.50}
    ]

def handle_image_submitted(event, broker):
    payload = event["payload"]
    image_id = payload["image_id"]
    path = payload["path"]

    objects = _fake_detect_objects(path)

    new_event = inference_completed(
        image_id=image_id,
        objects=objects,
    )
    return broker.publish(new_event)
