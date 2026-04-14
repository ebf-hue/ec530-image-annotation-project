# Subscribes to: image.submitted
# Publishes: inference.completed

from events import inference_completed


def handle_image_submitted(event, broker):
    # simulate inference on image
    pass