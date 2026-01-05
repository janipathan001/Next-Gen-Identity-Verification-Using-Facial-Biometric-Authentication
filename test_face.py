from services.face_service import capture_face_embedding

embedding = capture_face_embedding()

if embedding is not None:
    print("Face embedding captured!")
    print("Embedding length:", len(embedding))
else:
    print("No face captured")