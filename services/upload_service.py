# Publishes: image.submitted
# Triggered by: CLI / user input

from events import image_submitted

#publishes: image.submitted
def handle_cli_image(broker, image_id: str, path: str):
    event = image_submitted(image_id=image_id, path=path)
    print(f"[Upload_service] Uploaded image with image_id={image_id}")
    return broker.publish(event)
