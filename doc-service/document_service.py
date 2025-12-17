from fastapi import FastAPI, UploadFile, File, HTTPException
import boto3
import json
import os
import psycopg2
from kafka import KafkaProducer
from utils import get_secret

app = FastAPI()

# --- CONFIG ---
S3_BUCKET = "document-reader-storage-dev-mahmoud"
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
SECRET_NAME = "dev/doc-service/db_creds"
DB_NAME = "doc_db"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

# S3 Client
s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY,
                         aws_session_token=AWS_SESSION_TOKEN,
                         region_name='us-east-1')

# Kafka Producer
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
except Exception as e:
    print(f"Warning: Kafka unavailable ({e})")
    producer = None

def get_db_connection():
    try:
        print(f"Fetching credentials for {SECRET_NAME}...")
        creds = get_secret(SECRET_NAME)
        return psycopg2.connect(
            dbname=DB_NAME,
            user=creds['username'],
            password=creds['password'],
            host="learning-platform-db.csb4qs6smfo3.us-east-1.rds.amazonaws.com",
            port="5432"
        )
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = "test_user"):
    try:
        file_key = f"{user_id}/{file.filename}"
        s3_client.upload_fileobj(file.file, S3_BUCKET, file_key)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, user_id VARCHAR(255), filename VARCHAR(255), s3_url TEXT, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
        cur.execute("INSERT INTO documents (user_id, filename, s3_url) VALUES (%s, %s, %s)", (user_id, file.filename, f"s3://{S3_BUCKET}/{file_key}"))
        conn.commit()
        conn.close()

        if producer:
            event = {"document_id": file.filename, "s3_key": file_key, "user_id": user_id, "status": "UPLOADED"}
            producer.send('document.uploaded', value=event)

        return {"status": "success", "file_key": file_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
