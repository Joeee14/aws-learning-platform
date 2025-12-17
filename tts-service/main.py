from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import psycopg2
from kafka import KafkaProducer
from utils import get_secret

app = FastAPI()

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
SECRET_NAME = "dev/tts-service/db_creds"
DB_NAME = "tts_db"

try:
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER], value_serializer=lambda x: json.dumps(x).encode('utf-8'))
except:
    producer = None

class TTSRequest(BaseModel):
    text: str
    user_id: str

def get_db_connection():
    creds = get_secret(SECRET_NAME)
    return psycopg2.connect(dbname=DB_NAME, user=creds['username'], password=creds['password'], host="learning-platform-db.csb4qs6smfo3.us-east-1.rds.amazonaws.com", port="5432")

@app.post("/api/tts/synthesize")
async def synthesize_speech(request: TTSRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS speech_requests (id SERIAL PRIMARY KEY, user_id VARCHAR(255), text_snippet TEXT, status VARCHAR(50));")
        cur.execute("INSERT INTO speech_requests (user_id, text_snippet, status) VALUES (%s, %s, %s)", (request.user_id, request.text[:50], 'PENDING'))
        conn.commit()
        conn.close()

        if producer:
            producer.send('audio.generation.requested', value={"text": request.text, "user_id": request.user_id})

        return {"status": "queued", "text_preview": request.text[:20]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
