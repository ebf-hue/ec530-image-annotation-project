# Subscribes to: annotation.stored
# Publishes: embedding.created

from events import embedding_created

def handle_annotation_stored(event, broker):
    # simulate creating embedding + storing in vector DB
    pass