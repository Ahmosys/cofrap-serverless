import string, secrets, pyqrcode, io, base64, bcrypt, psycopg2, os
from datetime import datetime, UTC

# Global variable to hold the database connection
# This avoids reconnecting on every function call
dbConn = None

def initConnection():
    global dbConn
    if dbConn:
        return dbConn  # Return existing connection if already initialized
    # Read the PostgreSQL password from the OpenFaaS secret file
    with open('/var/openfaas/secrets/postgres-password', 'r') as s:
        pwd = s.read().strip()
    # Establish a new connection using environment variables for other credentials
    dbConn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'), 
        user=os.getenv('DB_USER'),
        password=pwd, 
        host=os.getenv('DB_HOST'), 
        port=os.getenv('DB_PORT')
    )
    return dbConn

def handle(event, context):
    # Extract the username from the request body
    username = event.body.strip()

    if not username:
        return {"statusCode": 400, "body": "Missing username"}

    # Convert the username to a string if it's a bytes object
    if isinstance(username, bytes):
        username = username.decode()

    # Generate a secure random password (24 characters) and hash it
    raw_pwd = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*()_+") for _ in range(24))
    hashed_pwd = bcrypt.hashpw(raw_pwd.encode(), bcrypt.gensalt()).decode()

    # Generate a QR code from the raw password
    qr = pyqrcode.create(raw_pwd)
    buffer = io.BytesIO()
    qr.png(buffer, scale=5)  # Save QR code as PNG in memory
    encoded_qrcode = base64.b64encode(buffer.getvalue()).decode()  # Encode PNG as base64 string

    # Initialize database connection
    conn = initConnection()
    cur = conn.cursor()
    # Create the users table if it doesn't exist
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        mfa TEXT,
        gendate BIGINT,
        expired BOOLEAN
    )""")
        
    # Insert or update the user record with the new password and generation date
    cur.execute("""INSERT INTO users (username, password, gendate, expired)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (username) DO UPDATE
        SET password = EXCLUDED.password,
            gendate = EXCLUDED.gendate,
            expired = False""",
        (username, hashed_pwd, int(datetime.now(UTC).timestamp()), False))
    # Commit changes and close the cursor
    conn.commit()
    cur.close() 
    
    # Return the QR code as a base64-encoded string in the response
    return {"statusCode": 200, "body": encoded_qrcode}
