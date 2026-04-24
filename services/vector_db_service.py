# Subscribes to: annotation.stored
# Publishes: embedding.created

from events import embedding_created
from pymongo import MongoClient

# mongodb setup (local)
client = MongoClient("mongodb://localhost:27017")
db = client["image_annotation"]
vectors_collection = db["vectors"] # like an sql table

def _fake_embedding(image_path: str) -> list:
    # arbitrary vector initialization
    vector = [0.5] * 7
    
    if "kitasan" in image_path and "black" in image_path:
        vector = [0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
        
    elif "almond" in image_path and "eye" in image_path:
        vector = [0.1, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1]
        
    elif "daitaku" in image_path and "helios" in image_path:
        vector = [0.1, 0.1, 0.9, 0.1, 0.1, 0.1, 0.1]
        
    elif "haru" in image_path and "urara" in image_path:
        vector = [0.1, 0.1, 0.1, 0.9, 0.1, 0.1, 0.1]
        
    elif "maruzensky" in image_path:
        vector = [0.1, 0.1, 0.1, 0.1, 0.9, 0.1, 0.1]
        
    elif "forever" in image_path and "young" in image_path:
        vector = [0.1, 0.1, 0.1, 0.1, 0.1, 0.9, 0.1]
        
    elif "rachel" in image_path or "alexandra" in image_path:
        vector = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.9]

    return vector

def handle_annotation_stored(event, broker):
    # simulate creating embedding + storing in vector DB
    payload = event["payload"]
    image_id = payload["image_id"]
    path = payload["path"]
    doc_id = payload["doc_id"]

    # fake embedding using our function
    vector = _fake_embedding(path)

    # insert to mongodb vectors table we made earlier
    vectors_collection.insert_one({
        "_id": image_id, # mongodb requires _id
        "doc_id": doc_id,
        "vector": vector
    })

    # publish the embedding created event
    new_event = embedding_created(image_id=image_id, vector=vector)
    return broker.publish(new_event)
