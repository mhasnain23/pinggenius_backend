from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from models.contact import contacts_collection

router = APIRouter(tags=["Contacts"])

# -------- Schema --------
class Contact(BaseModel):
    name: str
    linkedin_url: HttpUrl
    role: str
    company: str | None = None
    website: HttpUrl | None = None
    tone: str = "formal"
    selected_email: str

# -------- Route --------
@router.post("/save-contact")
async def save_contact(contact: Contact):
    try:
        contact_data = contact.dict()
        contact_data["created_at"] = datetime.utcnow()

        await contacts_collection.insert_one(contact_data)

        return {"status": "success", "message": "Contact saved!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
