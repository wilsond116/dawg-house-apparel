
from pymongo.mongo_client import MongoClient
import os
import dotenv
import certifi
import re
import uuid
# Connection setup
uri = os.environ.get("MONGO_URI")
client = MongoClient(uri, tlsCAFile=certifi.where())

# Test connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Slug generator
def generate(name):
    slug = re.sub(r'[^a-z0-9 ]', '', name.lower())
    slug = slug.replace(" ", "-")
    return slug

# Product setup
db = client["Products"]
products = db["product"]

#orders set up
orders_db = client["orders"]
orders = orders_db["order"]


product_data = [
    {
        "name": "Dawg Tee",
        "description": "A comfortable and stylish tee for everyday wear.",
        "price": 1.00,
        "category": "T-shirt",
        "stock": 100,
        "images": [
            "https://placehold.co/300x400?text=Black+Hoodie"
        ],
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["black"],
        "slug": generate("Dawg Tee")
    },
    {
"name": "Blue Dawg Tee",
        "description": "A comfortable and stylish tee for everyday wear.",
        "price": 1.00,
        "category": "T-shirt",
        "stock": 100,
        "images": [
            "https://placehold.co/300x400?text=Black+Hoodie"
        ],
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["black"],
        "slug": generate("Blue Dawg Tee")
    }

]

def insert_order(order):
    orders.insert_one(order)



#Make a data structure titled orders
#insert them here so they can get notified when they have an order

# Insert into MongoDB
#result = products.insert_many(product_data)
#print(f"Inserted {len(result.inserted_ids)} products!")
