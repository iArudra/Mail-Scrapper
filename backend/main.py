from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
import database

app = FastAPI(title="Support Email Intelligence API")

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    database.init_db()

class EmailCreate(BaseModel):
    message_id: str
    thread_id: str
    sender: str
    subject: str
    body: str
    category: str
    priority: str
    sentiment: str
    confidence: float
    suggested_reply: str
    status: str = "Open"
    created_at: str

class EmailResponse(EmailCreate):
    id: int

class StatusUpdate(BaseModel):
    status: str

class ReplyUpdate(BaseModel):
    suggested_reply: str

@app.post("/emails", response_model=dict)
async def create_email(email: EmailCreate):
    email_id = database.insert_email(email.dict())
    if email_id:
        return {"id": email_id, "message": "Email stored successfully"}
    else:
        raise HTTPException(status_code=400, detail="Email with this message_id already exists")

@app.get("/emails", response_model=List[EmailResponse])
async def get_emails():
    return database.get_all_emails()

@app.get("/emails/{id}", response_model=EmailResponse)
async def get_email(id: int):
    email = database.get_email_by_id(id)
    if email:
        return email
    raise HTTPException(status_code=404, detail="Email not found")

@app.patch("/emails/{id}/status")
async def update_status(id: int, status_update: StatusUpdate):
    success = database.update_email_status(id, status_update.status)
    if success:
        return {"message": f"Status updated to {status_update.status}"}
    raise HTTPException(status_code=404, detail="Email not found")

@app.patch("/emails/{id}/reply")
async def update_reply(id: int, reply_update: ReplyUpdate):
    success = database.update_suggested_reply(id, reply_update.suggested_reply)
    if success:
        return {"message": "Suggested reply updated"}
    raise HTTPException(status_code=404, detail="Email not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
