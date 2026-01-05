from db.mongo import users_collection

users_collection.insert_one({
    "name": "Test User",
    "email": "test@gmail.com"
})

print("MongoDB connection successful!")
