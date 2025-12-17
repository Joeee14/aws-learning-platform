from fastapi import FastAPI, UploadFile, File, HTTPException
import boto3
import json
import os
import psycopg2
from kafka import KafkaProducer
from utils import get_secret

app = FastAPI()

# --- CONFIG ---
S3_BUCKET = "stt-service-storage-dev" # Hypothetical bucket
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
SECRET_NAME = "dev/stt-service/db_creds"
DB_NAME = "stt_db"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, aws_session_token=AWS_SESSION_TOKEN, region_name='us-east-1')

try:
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER], value_serializer=lambda x: json.dumps(x).encode('utf-8'))
except:
    producer = None

def get_db_connection():
    creds = get_secret(SECRET_NAME)
    return psycopg2.connect(dbname=DB_NAME, user=creds['username'], password=creds['password'], host="learning-platform-db.csb4qs6smfo3.us-east-1.rds.amazonaws.com", port="5432")

@app.post("/api/stt/transcribe")
async def transcribe_audio(file: UploadFile = File(...), user_id: str = "test_user"):
    try:
        # 1. Upload Audio
        file_key = f"{user_id}/audio/{file.filename}"
        s3_client.upload_fileobj(file.file, S3_BUCKET, file_key)

        # 2. Save to DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS transcriptions (id SERIAL PRIMARY KEY, user_id VARCHAR(255), filename VARCHAR(255), status VARCHAR(50));")
        cur.execute("INSERT INTO transcriptions (user_id, filename, status) VALUES (%s, %s, %s)", (user_id, file.filename, 'PENDING'))
        conn.commit()
        conn.close()

        # 3. Kafka Event
        if producer:
            producer.send('audio.transcription.requested', value={"file_key": file_key, "user_id": user_id})

        return {"status": "queued", "file_key": file_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
