import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "support_emails.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            thread_id TEXT,
            sender TEXT,
            subject TEXT,
            body TEXT,
            category TEXT,
            priority TEXT,
            sentiment TEXT,
            confidence REAL,
            suggested_reply TEXT,
            status TEXT DEFAULT 'Open',
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_email(email_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO emails (
                message_id, thread_id, sender, subject, body, 
                category, priority, sentiment, confidence, 
                suggested_reply, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email_data['message_id'], email_data['thread_id'], email_data['sender'], 
            email_data['subject'], email_data['body'], email_data['category'], 
            email_data['priority'], email_data['sentiment'], email_data['confidence'], 
            email_data['suggested_reply'], email_data.get('status', 'Open'), 
            email_data['created_at']
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_all_emails():
    conn = get_db_connection()
    emails = conn.execute('SELECT * FROM emails ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(row) for row in emails]

def get_email_by_id(email_id):
    conn = get_db_connection()
    email = conn.execute('SELECT * FROM emails WHERE id = ?', (email_id,)).fetchone()
    conn.close()
    return dict(email) if email else None

def update_email_status(email_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE emails SET status = ? WHERE id = ?', (status, email_id))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

def update_suggested_reply(email_id, suggested_reply):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE emails SET suggested_reply = ? WHERE id = ?', (suggested_reply, email_id))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
