# models/contact.py

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client["pinggenius"]
contacts = db["contacts"]

async def save_contact_to_db(contact_data: dict):
    contact_data["created_at"] = datetime.utcnow()
    contact_data["status"] = "pending"
    contact_data["source"] = "linkedin"
    await contacts.insert_one(contact_data)
