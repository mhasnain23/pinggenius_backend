from fastapi import FastAPI

from api.v1.analyze_email import router as analyze_router
from api.v1 import generated_email
from gmail_service import fetch_recent_emails, get_gmail_service


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "PingGenius Email Agent API is running 🚀"}


app.include_router(analyze_router, prefix="/api/v1")
app.include_router(generated_email.router, prefix="/api/v1")


@app.get("/latest-emails")
def test_gmail():
    try:
        service = get_gmail_service()
        emails = fetch_recent_emails(service)
        return {"count": len(emails), "emails": emails}
    except Exception as e:
        return {"error": str(e)}
