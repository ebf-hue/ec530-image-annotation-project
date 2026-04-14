# Subscribes to: inference.completed
# Publishes: annotation.stored

from events import annotation_stored

def handle_inference_completed(event, broker):
    # simulate storing annotation in document DB
    pass