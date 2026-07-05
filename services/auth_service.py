import os
import logging
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger("pinmind.auth")

# 1. Initialize Firebase Admin SDK using cert certificate JSON path
service_account_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "firebase_service_account.json")
if os.path.exists(service_account_path):
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK successfully initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
else:
    logger.warning(f"Firebase Service account JSON not found at: {service_account_path}. Authentication falling back to local fallback mock.")

security_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    """
    Decodes and validates the Google Firebase ID Token from the Authorization Header.
    Yields validated user fields {uid, name, email, avatar_url}.
    """
    token = credentials.credentials
    
    # Dev Fallback if Admin SDK was unable to initialize
    if not firebase_admin._apps:
        logger.info("JWT Validation running in local offline demo bypass mode.")
        return {
            "uid": "mock_user_hackathon_demo",
            "name": "Hackathon Engineer",
            "email": "hackathon@pinmind.io",
            "avatar_url": "https://lh3.googleusercontent.com/a/ACg8ocLK"
        }
        
    try:
        # Decodes the token using Firebase's cached public keys
        decoded_token = auth.verify_id_token(token)
        return {
            "uid": decoded_token.get("uid"),
            "name": decoded_token.get("name"),
            "email": decoded_token.get("email"),
            "avatar_url": decoded_token.get("picture")
        }
    except Exception as e:
        logger.error(f"Token decryption failed: {e}")
        raise HTTPException(
            status_code=401, 
            detail="Session expired or signature validation failed. Please sign-in again."
        )
