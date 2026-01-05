from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["face_auth_db"]
users_collection = db["users"]
logs_collection = db["auth_logs"]