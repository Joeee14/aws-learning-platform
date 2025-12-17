from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import psycopg2
from utils import get_secret

app = FastAPI()

SECRET_NAME = "dev/chat-service/db_creds"
DB_NAME = "chat_db"

class ChatMessage(BaseModel):
    user_id: str
    message: str

def get_db_connection():
    creds = get_secret(SECRET_NAME)
    return psycopg2.connect(dbname=DB_NAME, user=creds['username'], password=creds['password'], host="learning-platform-db.csb4qs6smfo3.us-east-1.rds.amazonaws.com", port="5432")

@app.post("/api/chat/message")
async def send_message(chat: ChatMessage):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS chats (id SERIAL PRIMARY KEY, user_id VARCHAR(255), message TEXT, reply TEXT);")
        # Simulating a bot reply
        reply = f"Echo: {chat.message}"
        cur.execute("INSERT INTO chats (user_id, message, reply) VALUES (%s, %s, %s)", (chat.user_id, chat.message, reply))
        conn.commit()
        conn.close()

        return {"user": chat.message, "bot": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
