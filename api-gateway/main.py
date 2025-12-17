from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from utils import get_secret

app = FastAPI()

SECRET_NAME = "dev/api-gateway/db_creds"
DB_NAME = "user_db"

class UserCreate(BaseModel):
    username: str
    email: str

def get_db_connection():
    creds = get_secret(SECRET_NAME)
    return psycopg2.connect(dbname=DB_NAME, user=creds['username'], password=creds['password'], host="learning-platform-db.csb4qs6smfo3.us-east-1.rds.amazonaws.com", port="5432")

@app.post("/api/users/register")
async def register_user(user: UserCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(255), email VARCHAR(255));")
        cur.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (user.username, user.email))
        conn.commit()
        conn.close()
        return {"status": "created", "username": user.username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
