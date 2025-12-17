import boto3
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

SECRET_NAME = "dev/doc-service/db_creds"
REGION_NAME = "us-east-1"
HOST_NAME = "learning-platform-db.csb4qs6smfo3.us-east-1.rds.amazonaws.com"
REQUIRED_DBS = ["user_db", "chat_db", "doc_db", "quiz_db", "stt_db", "tts_db"]

def create_databases():
    print("--- DB SETUP START ---")
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=REGION_NAME)
    try:
        response = client.get_secret_value(SecretId=SECRET_NAME)
        creds = json.loads(response['SecretString'])
        conn = psycopg2.connect(host=HOST_NAME, database="postgres", user=creds['username'], password=creds['password'])
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        for db in REQUIRED_DBS:
            try:
                cur.execute(f"CREATE DATABASE {db};")
                print(f"Created {db}")
            except psycopg2.errors.DuplicateDatabase:
                print(f"Skipping {db} (Exists)")
        conn.close()
    except Exception as e:
        print(f"Setup Error: {e}")

if __name__ == "__main__":
    create_databases()
