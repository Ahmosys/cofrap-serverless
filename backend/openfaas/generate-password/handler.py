import string, secrets, pyqrcode, io, base64, bcrypt, psycopg2, os
from datetime import datetime, UTC

dbConn = None

def initConnection():
    global dbConn
    if dbConn:
        return dbConn
    with open('/var/openfaas/secrets/postgres-password', 'r') as s:
        pwd = s.read().strip()
    dbConn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'), 
        user=os.getenv('DB_USER'),
        password=pwd, 
        host=os.getenv('DB_HOST'), 
        port=os.getenv('DB_PORT')
    )
    return dbConn

def handle(event, context):
    # Gérer les requêtes OPTIONS pour le CORS preflight
    if event.method == "OPTIONS":
        return {
            "statusCode": 200,
            "body": "",
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        }

    username = event.body.strip()

    if not username:
        return {"statusCode": 400, "body": "Missing username"}

    if isinstance(username, bytes):
        username = username.decode()

    raw_pwd = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()_+") for _ in range(24))
    hashed_pwd = bcrypt.hashpw(raw_pwd.encode(), bcrypt.gensalt()).decode()

    qr = pyqrcode.create(raw_pwd)
    buffer = io.BytesIO()
    qr.png(buffer, scale=5)
    encoded_qrcode = base64.b64encode(buffer.getvalue()).decode()

    conn = initConnection()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        mfa TEXT,
        gendate BIGINT,
        expired BOOLEAN
    )""")
        
    cur.execute("""INSERT INTO users (username, password, gendate, expired)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE
        SET password = EXCLUDED.password,
            gendate = EXCLUDED.gendate,
            expired = False""",
        (username, hashed_pwd, int(datetime.now(UTC).timestamp()), False))
    conn.commit()
    cur.close() 
    
    return {
        "statusCode": 200,
        "body": encoded_qrcode,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "text/plain"
        }
    }
