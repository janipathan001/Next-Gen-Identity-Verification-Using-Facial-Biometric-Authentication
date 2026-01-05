from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["face_auth_db"]
users_collection = db["users"]
login_logs_collection = db["login_logs"]