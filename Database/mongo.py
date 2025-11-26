#To recieve
# db/mongo.py
import os
from pymongo.mongo_client import MongoClient
import certifi

# Connection URI
uri = os.environ.get("MONGO_URI")

# Create client
client = MongoClient(uri, tlsCAFile=certifi.where())

# Ping the server to test
try:
    client.admin.command('ping')
    print("Connected to MongoDB!")
except Exception as e:
    print("MongoDB connection failed:", e)

# Exported collections
db = client["Products"]
product_collection = db["product"]



