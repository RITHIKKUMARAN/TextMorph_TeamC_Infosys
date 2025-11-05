import os
from pymongo import MongoClient
from dotenv import load_dotenv
import hashlib

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["textmorph_db"]
users = db["users"]

# Function to hash passwords before saving
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register user
def register_user(username, password):
    if users.find_one({"username": username}):
        return False, "User already exists!"
    users.insert_one({
        "username": username,
        "password": hash_password(password)
    })
    return True, "User registered successfully!"

# Login user
def login_user(username, password):
    hashed = hash_password(password)
    user = users.find_one({"username": username, "password": hashed})
    if user:
        return True, "Login successful!"
    return False, "Invalid username or password."
