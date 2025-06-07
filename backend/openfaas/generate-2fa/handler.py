import pyqrcode, base64, io, os, psycopg2
from cryptography.fernet import Fernet
import pyotp

dbConn = None

# Initialize DB connection if not already done
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
    # Handle CORS pre-flight request
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

    # Extract the username from the request body
    username = event.body.strip()
    if not username:
        return {
            "statusCode": 400,
            "body": "Missing username",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Convert the username to a string if it's a bytes object
    if isinstance(username, bytes):
        username = username.decode()
    
    # Initialize database connection
    conn = initConnection()
    cur = conn.cursor()
    
    # Check if user exists
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    if not cur.fetchone():
        cur.close()
        return {
            "statusCode": 404,
            "body": "User not found",
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Generate a random secret
    secret = pyotp.random_base32()

    # Create a QR code from the TOTP URI
    qr = pyqrcode.create(pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="CofrapAuth"))
    buffer = io.BytesIO()
    qr.png(buffer, scale=5)
    encoded_qr = base64.b64encode(buffer.getvalue()).decode()

    # Encrypt the secret
    with open('/var/openfaas/secrets/mfa-key', 'r') as s:
        mfa_key = s.read().strip()
    fernet = Fernet(mfa_key.encode())
    enc_secret = fernet.encrypt(secret.encode()).decode()
    
    # Update the user with the encrypted secret
    cur.execute("UPDATE users SET mfa=%s WHERE username=%s", (enc_secret, username))
    conn.commit()
    cur.close()

    # Return the QR code image encoded in base64
    return {
        "statusCode": 200,
        "body": encoded_qr,
        "headers": {
            "Content-Type": "text/plain",
            "Access-Control-Allow-Origin": "*"
        }
    }
