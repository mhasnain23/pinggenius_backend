from datetime import datetime
from database.mongo import hard_emails

async def save_hard_email_to_db(email_data: dict):
    email_data["type"] = "inbound"
    email_data["source"] = "gmail"
    email_data["status"] = "hard"
    email_data["created_at"] = datetime.utcnow()
    await hard_emails.insert_one(email_data)
