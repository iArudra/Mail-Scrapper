import requests
from datetime import datetime
import json

API_URL = "http://localhost:8000"

test_emails = [
    {
        "message_id": "msg_001",
        "thread_id": "thr_001",
        "sender": "john.doe@example.com",
        "subject": "Login Issue",
        "body": "I cannot login to my account. It says 'Invalid password' even though I'm sure it's correct.",
        "category": "Technical Support",
        "priority": "High",
        "sentiment": "Negative",
        "confidence": 0.98,
        "suggested_reply": "Hello John, we are sorry to hear you're having trouble. Please try resetting your password using the 'Forgot Password' link.",
        "status": "Open",
        "created_at": datetime.now().isoformat()
    },
    {
        "message_id": "msg_002",
        "thread_id": "thr_002",
        "sender": "jane.smith@example.com",
        "subject": "Billing Question",
        "body": "I was charged twice for this month's subscription. Can you please check?",
        "category": "Billing",
        "priority": "High",
        "sentiment": "Negative",
        "confidence": 0.95,
        "suggested_reply": "Hello Jane, we've identified the double charge and have initiated a refund for the extra amount.",
        "status": "Open",
        "created_at": datetime.now().isoformat()
    },
    {
        "message_id": "msg_003",
        "thread_id": "thr_003",
        "sender": "bob.builder@example.com",
        "subject": "Feature Request: Dark Mode",
        "body": "The app is great, but a dark mode would be awesome for late-night work.",
        "category": "Feature Request",
        "priority": "Low",
        "sentiment": "Positive",
        "confidence": 0.90,
        "suggested_reply": "Hello Bob, thank you for the suggestion! We've added Dark Mode to our roadmap.",
        "status": "Open",
        "created_at": datetime.now().isoformat()
    }
]

def seed_data():
    for email in test_emails:
        try:
            response = requests.post(f"{API_URL}/emails", json=email)
            if response.status_code == 200:
                print(f"Successfully added: {email['subject']}")
            else:
                print(f"Failed to add: {email['subject']} - {response.text}")
        except Exception as e:
            print(f"Error seeding {email['subject']}: {e}")

if __name__ == "__main__":
    seed_data()
