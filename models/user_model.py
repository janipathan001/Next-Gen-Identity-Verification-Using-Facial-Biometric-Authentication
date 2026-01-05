from db.mongo import users_collection, login_logs_collection
from services.face_service import capture_face_embedding
import bcrypt
from datetime import datetime

def register_user(name, email, password):
    # Check if user already exists
    if users_collection.find_one({"email": email}):
        return False, "User already exists"

    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    print("Capturing face... Please look at the camera")
    face_embedding = capture_face_embedding()
    
    if face_embedding is None:
        return False, "Face not detected"

    # Convert numpy array to list before storing in MongoDB
    face_embedding_list = face_embedding.tolist()

    user_data = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "face_embedding": face_embedding_list,
        "created_at": datetime.utcnow()
    }

    users_collection.insert_one(user_data)
    return True, "User registered successfully"