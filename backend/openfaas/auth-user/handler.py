import os, time, psycopg2, bcrypt, pyotp
from cryptography.fernet import Fernet

dbConn = None

# Initialize the database connection
def initConnection():
    global dbConn
    if dbConn:
        return dbConn
    with open('/var/openfaas/secrets/postgres-password', 'r') as s:
        password = s.read().strip()
    dbConn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=password,
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return dbConn

def handle(event, context):
    # Handle CORS preflight request
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

    # Extract the username, password, and OTP from the request body
    payload = event.body.decode('utf-8').strip().split(",")
    username, password, otp = payload[0], payload[1], payload[2]

    # Initialize database connection
    conn = initConnection()
    cur = conn.cursor()

    # Check if user exists
    cur.execute("SELECT password, mfa, gendate FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    if not row:
        return {
            "statusCode": 404,
            "body": "User not found",
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    stored_hash, enc_mfa, gendate = row

    # Check if password has expired (6 months)
    if time.time() - gendate > 6 * 30 * 24 * 3600:
        cur.execute("UPDATE users SET expired=True WHERE username=%s", (username,))
        conn.commit()
        return {
            "statusCode": 403,
            "body": "Password expired",
            "headers": {"Access-Control-Allow-Origin": "*"}
        }
    
    # Check if password is correct
    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return {
            "statusCode": 401,
            "body": "Invalid password",
            "headers": {"Access-Control-Allow-Origin": "*"}
        }
    
    # Check if OTP is correct
    with open('/var/openfaas/secrets/mfa-key', 'r') as s:
        mfa_key = s.read().strip()
    secret = Fernet(mfa_key.encode()).decrypt(enc_mfa.encode()).decode()

    if not pyotp.TOTP(secret).verify(otp):
        return {
            "statusCode": 401,
            "body": "Invalid OTP",
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    # Return success
    return {
        "statusCode": 200,
        "body": "Authenticated",
        "headers": {"Access-Control-Allow-Origin": "*"}
    }
