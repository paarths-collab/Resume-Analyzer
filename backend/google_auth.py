from google.oauth2 import id_token
from google.auth.transport import requests
import os
from backend.database import get_db_cursor
from datetime import datetime, timedelta
import secrets

class GoogleAuthService:
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not self.client_id:
            print("Warning: GOOGLE_CLIENT_ID not configured")
    
    def verify_google_token(self, token: str) -> dict:
        """Verify Google ID token and return user info"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'full_name': idinfo.get('name'),
                'profile_picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
        except Exception as e:
            raise ValueError(f"Invalid Google token: {str(e)}")
    
    def google_signin(self, google_token: str) -> dict:
        """Sign in or sign up user with Google"""
        # Verify Google token
        google_user = self.verify_google_token(google_token)
        
        with get_db_cursor() as cursor:
            # Check if user exists
            cursor.execute(
                "SELECT id, email, full_name, google_id, profile_picture FROM users WHERE email = %s",
                (google_user['email'],)
            )
            user = cursor.fetchone()
            
            if user:
                # User exists - update Google info if needed
                if not user['google_id']:
                    cursor.execute(
                        """
                        UPDATE users 
                        SET google_id = %s, profile_picture = %s, 
                            email_verified = TRUE, auth_provider = 'google', updated_at = NOW()
                        WHERE id = %s
                        """,
                        (google_user['google_id'], google_user['profile_picture'], user['id'])
                    )
                
                user_id = user['id']
                email = user['email']
                full_name = user['full_name']
            else:
                # Create new user
                cursor.execute(
                    """
                    INSERT INTO users (email, google_id, full_name, profile_picture, 
                                     auth_provider, email_verified)
                    VALUES (%s, %s, %s, %s, 'google', TRUE)
                    RETURNING id, email, full_name
                    """,
                    (google_user['email'], google_user['google_id'], 
                     google_user['full_name'], google_user['profile_picture'])
                )
                new_user = cursor.fetchone()
                user_id = new_user['id']
                email = new_user['email']
                full_name = new_user['full_name']
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expiry_hours = int(os.getenv('SESSION_EXPIRY_HOURS', 24))
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            
            cursor.execute(
                """
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, %s)
                """,
                (user_id, session_token, expires_at)
            )
            
            return {
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name
                },
                'session_token': session_token,
                'expires_at': expires_at.isoformat()
            }

google_auth_service = GoogleAuthService()