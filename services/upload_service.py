# Publishes: image.submitted
# Triggered by: CLI / user input

from events import image_submitted

#publishes: image.submitted
def handle_cli_image(broker, image_id: str, path: str):
    event = image_submitted(image_id=image_id, path=path)
    return broker.publish(event)
