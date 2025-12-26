from pymongo import MongoClient
from app.config import settings

class Database:
    client: MongoClient = None

    def connect(self):
        self.client = MongoClient(settings.MONGODB_URI)
        print("Connected to MongoDB")

    def get_db(self):
        return self.client[settings.DB_NAME]

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

db = Database()

def get_database():
    return db.get_db()

