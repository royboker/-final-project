from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client["docuguard"]

users_collection = db["users"]
scans_collection = db["scans"]

# בדיקה אמיתית של החיבור
client.admin.command("ping")

print("✅ Connected to MongoDB")