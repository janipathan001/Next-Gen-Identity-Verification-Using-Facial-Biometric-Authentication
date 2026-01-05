from db.mongo import users_collection, login_logs_collection
from services.face_service import capture_face_embedding, compare_faces
import bcrypt
from datetime import datetime
import numpy as np

def login_user(email, password):
    user = users_collection.find_one({"email": email})

    if not user:
        login_logs_collection.insert_one({
            "email": email,
            "status": "failed",
            "reason": "User not found",
            "timestamp": datetime.utcnow()
        })
        return False, "User not found"

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        login_logs_collection.insert_one({
            "email": email,
            "status": "failed",
            "reason": "Wrong password",
            "timestamp": datetime.utcnow()
        })
        return False, "Invalid password"

    print("Verifying face... Please look at the camera")
    live_embedding = capture_face_embedding()

    if live_embedding is None:
        login_logs_collection.insert_one({
            "email": email,
            "status": "failed",
            "reason": "Face not detected",
            "timestamp": datetime.utcnow()
        })
        return False, "Face not detected"

    # Convert stored embedding back to numpy array
    stored_embedding = np.array(user["face_embedding"])

    match = compare_faces(stored_embedding, live_embedding)

    if not match:
        login_logs_collection.insert_one({
            "email": email,
            "status": "failed",
            "reason": "Face mismatch",
            "timestamp": datetime.utcnow()
        })
        return False, "Face verification failed"

    # ✅ SUCCESS LOG
    login_logs_collection.insert_one({
        "email": email,
        "status": "success",
        "timestamp": datetime.utcnow()
    })

    return True, user