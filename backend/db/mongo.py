from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["docuguard"]

users_collection = db["users"]
scans_collection = db["scans"]
chat_sessions_collection = db["chat_sessions"]
chat_messages_collection = db["chat_messages"]

try:
    client.admin.command("ping")
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"⚠️ MongoDB connection warning: {e}")