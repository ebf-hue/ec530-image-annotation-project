import pytest
from unittest.mock import MagicMock
from services.inference_service import handle_image_submitted
from services.document_db_service import handle_inference_completed
from services.vector_db_service import handle_annotation_stored
from events import image_submitted, inference_completed, annotation_stored

# test inference service
class TestInferenceService:
  def test_image_submitted_publishes_event(self):
    #

# test document db service
class TestDocumentDBService:
  def test_inference_completed_stores_doc(self):
    #

  # big word idempotency
  def test_idempotency_inference_does_not_duplicate_doc(self):
    #

# test vector db service
class TestVectorDBService:
  def test_annotation_stored_publishes_embedding(self):
    #
