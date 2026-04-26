from unittest.mock import MagicMock, patch

from events import image_submitted, inference_completed, annotation_stored, query_submitted
from services.inference_service import handle_image_submitted
from services.document_db_service import handle_inference_completed, get_document
from services.vector_db_service import handle_annotation_stored
from services.upload_service import handle_cli_image
from services.cli import simulate_upload, simulate_query
from services.query_service import handle_query_submitted


class TestInferenceService:
    def test_image_submitted_publishes_event(self):
        broker = MagicMock()

        event = image_submitted("img_001", "images/street.jpg")
        handle_image_submitted(event, broker)

        broker.publish.assert_called_once()
        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "inference.completed"
        assert published_event["payload"]["image_id"] == "img_001"
        assert published_event["payload"]["path"] == "images/street.jpg"
        assert len(published_event["payload"]["objects"]) > 0
        assert published_event["payload"]["objects"][0]["label"] == "car"


class TestDocumentDBService:
    @patch("services.document_db_service.annotations_collection")
    def test_inference_completed_stores_doc(self, mock_annotations_collection):
        broker = MagicMock()

        event = inference_completed(
            image_id="img_001",
            objects=[{"label": "car", "bbox": [12, 44, 188, 200], "conf": 0.93}],
            path="images/street.jpg",
        )

        handle_inference_completed(event, broker)

        mock_annotations_collection.replace_one.assert_called_once()

        query_arg, doc_arg = mock_annotations_collection.replace_one.call_args[0][:2]
        options = mock_annotations_collection.replace_one.call_args[1]

        assert query_arg == {"_id": "img_001"}
        assert doc_arg["_id"] == "img_001"
        assert doc_arg["image_id"] == "img_001"
        assert doc_arg["path"] == "images/street.jpg"
        assert doc_arg["objects"][0]["label"] == "car"
        assert doc_arg["review"]["status"] == "uncorrected"
        assert options["upsert"] is True

        broker.publish.assert_called_once()
        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "annotation.stored"
        assert published_event["payload"]["image_id"] == "img_001"
        assert published_event["payload"]["doc_id"] == "doc_img_001"
        assert published_event["payload"]["path"] == "images/street.jpg"

    @patch("services.document_db_service.annotations_collection")
    def test_idempotency_uses_replace_one_upsert(self, mock_annotations_collection):
        broker = MagicMock()

        event = inference_completed(
            image_id="img_001",
            objects=[{"label": "car", "bbox": [12, 44, 188, 200], "conf": 0.93}],
            path="images/street.jpg",
        )

        handle_inference_completed(event, broker)
        handle_inference_completed(event, broker)

        assert mock_annotations_collection.replace_one.call_count == 2
        assert broker.publish.call_count == 2

        for call in mock_annotations_collection.replace_one.call_args_list:
            assert call.args[0] == {"_id": "img_001"}
            assert call.kwargs["upsert"] is True

    @patch("services.document_db_service.annotations_collection")
    def test_get_document_reads_from_mongo_collection(self, mock_annotations_collection):
        mock_annotations_collection.find_one.return_value = {
            "_id": "img_001",
            "image_id": "img_001",
        }

        doc = get_document("img_001")

        mock_annotations_collection.find_one.assert_called_once_with({"_id": "img_001"})
        assert doc["image_id"] == "img_001"


class TestVectorDBService:
    @patch("services.vector_db_service.vectors_collection")
    def test_annotation_stored_publishes_embedding(self, mock_vectors_collection):
        broker = MagicMock()

        event = annotation_stored(
            image_id="img_001",
            doc_id="doc_img_001",
            path="images/kitasan_black.jpg",
        )

        handle_annotation_stored(event, broker)

        mock_vectors_collection.replace_one.assert_called_once()

        broker.publish.assert_called_once()
        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "embedding.created"
        assert published_event["payload"]["image_id"] == "img_001"
        assert published_event["payload"]["vector"] == [0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

class TestUploadService:
    def test_handle_cli_image_publishes_image_submitted(self):
        broker = MagicMock()

        handle_cli_image(broker, image_id="img_001", path="images/street.jpg")

        broker.publish.assert_called_once()
        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "image.submitted"
        assert published_event["payload"]["image_id"] == "img_001"
        assert published_event["payload"]["path"] == "images/street.jpg"


class TestCLIService:
    @patch("builtins.input", side_effect=["img_001", "images/street.jpg"])
    @patch("builtins.print")
    def test_simulate_upload_publishes_image_event(self, mock_print, mock_input):
        broker = MagicMock()
        broker.publish.return_value = True

        simulate_upload(broker)

        broker.publish.assert_called_once()
        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "image.submitted"
        assert published_event["payload"]["image_id"] == "img_001"
        assert published_event["payload"]["path"] == "images/street.jpg"

        mock_print.assert_called_with("Submitted image img_001")

    @patch("builtins.input", side_effect=["horse", "3"])
    @patch("builtins.print")
    def test_simulate_query_publishes_query_event(self, mock_print, mock_input):
        broker = MagicMock()
        broker.publish.return_value = True

        simulate_query(broker)

        broker.publish.assert_called_once()
        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "query.submitted"
        assert published_event["payload"]["query_text"] == "horse"
        assert published_event["payload"]["top_k"] == 3

        mock_print.assert_called_with("Submitted query 'horse'")

    @patch("builtins.input", side_effect=["horse", ""])
    @patch("builtins.print")
    def test_simulate_query_defaults_top_k_to_4(self, mock_print, mock_input):
        broker = MagicMock()
        broker.publish.return_value = True

        simulate_query(broker)

        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "query.submitted"
        assert published_event["payload"]["query_text"] == "horse"
        assert published_event["payload"]["top_k"] == 4

class TestQueryService:
    @patch("services.query_service.vectors_collection")
    def test_query_submitted_returns_top_k_results(self, mock_vectors_collection):
        broker = MagicMock()

        mock_vectors_collection.find.return_value.limit.return_value = [
            {"_id": "img_001", "doc_id": "doc_img_001", "vector": [0.1, 0.2]},
            {"_id": "img_002", "doc_id": "doc_img_002", "vector": [0.3, 0.4]},
        ]

        event = query_submitted(query_text="horse", top_k=2)

        handle_query_submitted(event, broker)

        mock_vectors_collection.find.assert_called_once()
        mock_vectors_collection.find.return_value.limit.assert_called_once_with(2)

        broker.publish.assert_called_once()
        published_event = broker.publish.call_args[0][0]

        assert published_event["topic"] == "query.completed"
        assert published_event["payload"]["query_text"] == "horse"
        assert published_event["payload"]["results"] == ["img_001", "img_002"]