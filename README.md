# ec530-image-annotation-project
Event-driven image annotation project using AI and vector databases.

### System Components ###
- Defined events
- Messaging & bus broker
- Document DB
- Vector DB (Embedding Service)
- Annotation service
- Inference service
- Upload service
- CLI

### Features & Limitations ###
The system's components communicate with each other through the broker. The image retrieval in response to user queries is mocked. The flow through CLI, upload_service, inference_service, documentDB, vectorDB is functional. However, image results will currently be the top k documents in the database regardless of query contents.

#### Elena Berrios eberrios@bu.edu and Louis Jimenez-Hernandez louisjh@bu.edu ####
