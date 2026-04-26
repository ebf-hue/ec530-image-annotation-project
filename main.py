import threading
import time

from broker import Broker
from events import query_submitted

from services.upload_service import handle_cli_image
from services.inference_service import handle_image_submitted
from services.document_db_service import handle_inference_completed, annotations_collection
from services.vector_db_service import handle_annotation_stored, vectors_collection
from services.query_service import handle_query_submitted


# Used to let the CLI wait until the async upload pipeline finishes
pipeline_done = threading.Event()

#Marks the pipeline as being completed
def pipeline_finished(event):
    pipeline_done.set()

def main():
    broker = Broker()

    #Establish broker subscriptions
    broker.subscribe("image.submitted", lambda e: handle_image_submitted(e, broker))
    broker.subscribe("inference.completed", lambda e: handle_inference_completed(e, broker))
    broker.subscribe("annotation.stored", lambda e: handle_annotation_stored(e, broker))
    broker.subscribe("embedding.created", pipeline_finished)
    broker.subscribe("query.submitted", lambda e: handle_query_submitted(e, broker))
    broker.subscribe("query.completed", pipeline_finished)

    listener_thread = threading.Thread(
        target=broker.listen,
        daemon=True,
    )
    listener_thread.start()

    time.sleep(0.5)

    print("=== Image Annotation System ===")

    while True:
        print("\nChoose an option:")
        print("1. Upload Image")
        print("2. Run Query")
        print("3, Show DocumentDB")
        print("4, Show VectorDB")
        print("5. Exit")

        choice = input("> ").strip()

        #Upload image flow
        if choice == "1":
            image_id = input("Enter image ID: ").strip()
            path = input("Enter image path: ").strip()

            if not image_id or not path:
                print("Invalid input. Try again.")
                continue
            
            #Marks pipeline as not finished
            pipeline_done.clear()

            #Begins flow of CLI -> upload_service -> inference_service -> documentDB -> VectorDB
            handle_cli_image(broker, image_id=image_id, path=path)

            #Waits for pipeline to complete
            pipeline_done.wait()

        elif choice == "2":
            query_text = input("Enter search query: ").strip()
            top_k_input = input("Enter top_k (default 4): ").strip()

            top_k = int(top_k_input) if top_k_input.isdigit() else 4

             #Marks pipeline as not finished
            pipeline_done.clear()

            #Begins flow of CLI -> query_service
            event = query_submitted(query_text=query_text, top_k=top_k)
            broker.publish(event)

            #Waits for pipeline to complete
            pipeline_done.wait()

        elif choice == "3":
            print(list(annotations_collection.find()))

        elif choice == "4":
            print(list(vectors_collection.find()))

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()