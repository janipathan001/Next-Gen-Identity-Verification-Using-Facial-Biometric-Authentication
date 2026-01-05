import cv2
import numpy as np
import face_recognition

def capture_face_embedding():
    """
    Captures a face from webcam and returns a 128-d embedding.
    Returns None if no face is detected.
    """
    cap = cv2.VideoCapture(0)
    print("Please look at the camera. Press 'q' to capture.")

    embedding = None
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # detect face locations
            face_locations = face_recognition.face_locations(rgb_frame)
            if face_locations:
                # compute encodings using the small model for compatibility
                encodings = face_recognition.face_encodings(rgb_frame, face_locations, model="small")
                if encodings:
                    embedding = encodings[0]
                    print("Face captured successfully!")
                else:
                    print("Face detected but encoding failed. Try again.")
            else:
                print("No face detected. Try again.")
            break

    cap.release()
    cv2.destroyAllWindows()
    return embedding


def compare_faces(stored_embedding, live_embedding, threshold=0.6):
    """
    Compare two 128-d embeddings using Euclidean distance.
    Returns True if distance <= threshold.
    """
    if stored_embedding is None or live_embedding is None:
        return False

    stored_embedding = np.array(stored_embedding)
    live_embedding = np.array(live_embedding)

    if stored_embedding.shape != live_embedding.shape:
        raise ValueError(f"Embedding shapes do not match: {stored_embedding.shape} vs {live_embedding.shape}")

    distance = np.linalg.norm(stored_embedding - live_embedding)
    return distance <= threshold