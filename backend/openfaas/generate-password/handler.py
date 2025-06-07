import string
import secrets
import pyqrcode
import io
import base64
import bcrypt
import psycopg2
import os
import json

from typing import Optional, Dict, Any
from datetime import datetime, UTC
from psycopg2.extensions import connection as PGConnection

dbConn: Optional[PGConnection] = None

def init_connection() -> PGConnection:
    """
    Initializes and returns a singleton PostgreSQL database connection.
    """
    global dbConn
    if dbConn:
        return dbConn

    with open('/var/openfaas/secrets/postgres-password', 'r') as secret_file:
        password = secret_file.read().strip()

    dbConn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=password,
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return dbConn

def generate_password(length: int = 24) -> str:
    """
    Generates a secure random password of specified length.
    """
    charset = string.ascii_letters + string.digits + "!@#$%^&*()_+"
    return ''.join(secrets.choice(charset) for _ in range(length))

def generate_qrcode_base64(data: str) -> str:
    """
    Generates a QR code in PNG format and returns it as a base64-encoded string.
    """
    qr = pyqrcode.create(data)
    buffer = io.BytesIO()
    qr.png(buffer, scale=5)
    return base64.b64encode(buffer.getvalue()).decode()

def handle(event: Any, context: Any) -> Dict[str, Any]:
    """
    Handles an HTTP request to register or update a user in the database.
    Accepts JSON body with {"username": "..."}.
    Returns a base64-encoded QR code (no raw password exposed).
    """
    if event.method == "OPTIONS":
        # Handle CORS preflight
        return {
            "statusCode": 200,
            "body": "",
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        }

    # Parse JSON input body
    try:
        data = json.loads(event.body)
        username: str = data.get("username", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON format"}),
            "headers": {"Content-Type": "application/json"}
        }

    if not username:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing username"}),
            "headers": {"Content-Type": "application/json"}
        }

    # Generate password and QR code (only QR code is returned)
    raw_password: str = generate_password()
    hashed_password: str = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()
    qrcode_b64: str = generate_qrcode_base64(raw_password)

    try:
        conn = init_connection()
        cur = conn.cursor()

        # Create users table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                mfa TEXT,
                gendate BIGINT,
                expired BOOLEAN
            )
        """)

        # Insert or update user data
        cur.execute("""
            INSERT INTO users (username, password, gendate, expired)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE
            SET password = EXCLUDED.password,
                gendate = EXCLUDED.gendate,
                expired = FALSE
        """, (username, hashed_password, int(datetime.now(UTC).timestamp()), False))

        conn.commit()
        cur.close()
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Database error", "details": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "username": username,
            "qrcode_base64": qrcode_b64
        }),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        }
    }
