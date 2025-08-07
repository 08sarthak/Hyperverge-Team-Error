from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from api.db.user import insert_or_return_user
from api.utils.db import get_new_db_connection
from api.models import UserLoginData
from google.oauth2 import id_token
from google.auth.transport import requests
from api.settings import settings
import os

router = APIRouter()


@router.post("/login")
async def login_or_signup_user(user_data: UserLoginData) -> Dict:
    print(f"=== BACKEND AUTH DEBUG ===")
    print(f"Email: {user_data.email}")
    print(f"Given name: {user_data.given_name}")
    print(f"Family name: {user_data.family_name}")
    print(f"ID token exists: {bool(user_data.id_token)}")
    print(f"ID token length: {len(user_data.id_token) if user_data.id_token else 0}")
    print(f"ID token first 20 chars: {user_data.id_token[:20] if user_data.id_token else 'NONE'}")
    print(f"Google Client ID: {settings.google_client_id}")
    
    # Verify the Google ID token
    try:
        # Get Google Client ID from environment variable
        if not settings.google_client_id:
            print("ERROR: Google Client ID not configured")
            raise HTTPException(
                status_code=500, detail="Google Client ID not configured"
            )

        print("Attempting to verify token with Google...")
        
        # Verify the token with Google
        id_info = id_token.verify_oauth2_token(
            user_data.id_token, requests.Request(), settings.google_client_id
        )
        
        print(f"Token verified! Token email: {id_info.get('email')}")
        print(f"Token audience: {id_info.get('aud')}")

        # Check that the email in the token matches the provided email
        if id_info["email"] != user_data.email:
            print(f"ERROR: Email mismatch - token: {id_info['email']}, provided: {user_data.email}")
            raise HTTPException(
                status_code=401, detail="Email in token doesn't match provided email"
            )

    except ValueError as e:
        # Invalid token
        print(f"ERROR: Token verification failed - {str(e)}")
        raise HTTPException(
            status_code=401, detail=f"Invalid authentication token: {str(e)}"
        )

    # If token is valid, proceed with user creation/retrieval
    async with get_new_db_connection() as conn:
        cursor = await conn.cursor()
        user = await insert_or_return_user(
            cursor,
            user_data.email,
            user_data.given_name,
            user_data.family_name or "",
        )
        await conn.commit()

    print(f"User created/retrieved: {user}")
    return user
