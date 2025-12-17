from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import psycopg2
from kafka import KafkaProducer
from utils import get_secret

app = FastAPI()

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")
SECRET_NAME = "dev/quiz-service/db_creds"
DB_NAME = "quiz_db"

try:
    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER], value_serializer=lambda x: json.dumps(x).encode('utf-8'))
except:
    producer = None

class QuizRequest(BaseModel):
    document_id: str
    user_id: str

def get_db_connection():
    creds = get_secret(SECRET_NAME)
    return psycopg2.connect(dbname=DB_NAME, user=creds['username'], password=creds['password'], host="learning-platform-db.csb4qs6smfo3.us-east-1.rds.amazonaws.com", port="5432")

@app.post("/api/quiz/generate")
async def generate_quiz(request: QuizRequest):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS quizzes (id SERIAL PRIMARY KEY, user_id VARCHAR(255), doc_id VARCHAR(255), status VARCHAR(50));")
        cur.execute("INSERT INTO quizzes (user_id, doc_id, status) VALUES (%s, %s, %s)", (request.user_id, request.document_id, 'GENERATING'))
        conn.commit()
        conn.close()

        if producer:
            producer.send('quiz.requested', value={"doc_id": request.document_id, "user_id": request.user_id})

        return {"status": "processing", "doc_id": request.document_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
