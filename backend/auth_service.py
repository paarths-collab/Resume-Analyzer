from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
from datetime import datetime, timedelta
from backend.database import get_db_cursor
from backend.email_validator import email_validator
import os

ph = PasswordHasher()

class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using Argon2"""
        return ph.hash(password)
    
    @staticmethod
    def verify_password(password_hash: str, password: str) -> bool:
        """Verify password against hash"""
        try:
            ph.verify(password_hash, password)
            return True
        except VerifyMismatchError:
            return False
    
    @staticmethod
    def generate_token() -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(32)
    
    def signup(self, email: str, password: str, full_name: str = None) -> dict:
        """Create new user account"""
        # Validate email
        is_valid, error_msg = email_validator.validate_email(email)
        if not is_valid:
            raise ValueError(error_msg)
        
        with get_db_cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                raise ValueError("User with this email already exists")
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Insert user
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, full_name, auth_provider)
                VALUES (%s, %s, %s, 'email')
                RETURNING id, email, full_name, created_at
                """,
                (email, password_hash, full_name)
            )
            
            user = cursor.fetchone()
            return dict(user)
    
    def login(self, email: str, password: str) -> dict:
        """Authenticate user and create session"""
        with get_db_cursor() as cursor:
            # Get user
            cursor.execute(
                """
                SELECT id, email, password_hash, full_name, is_active
                FROM users WHERE email = %s
                """,
                (email,)
            )
            user = cursor.fetchone()
            
            if not user:
                raise ValueError("Invalid credentials")
            
            if not user['is_active']:
                raise ValueError("Account is deactivated")
            
            # Verify password
            if not self.verify_password(user['password_hash'], password):
                raise ValueError("Invalid credentials")
            
            # Create session
            session_token = self.generate_token()
            expiry_hours = int(os.getenv('SESSION_EXPIRY_HOURS', 24))
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            
            cursor.execute(
                """
                INSERT INTO user_sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, %s)
                """,
                (user['id'], session_token, expires_at)
            )
            
            return {
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name']
                },
                'session_token': session_token,
                'expires_at': expires_at.isoformat()
            }
    
    def verify_session(self, session_token: str) -> dict:
        """Verify and return user from session token"""
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT u.id, u.email, u.full_name, s.expires_at
                FROM user_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = %s AND s.expires_at > NOW()
                """,
                (session_token,)
            )
            
            session = cursor.fetchone()
            if not session:
                raise ValueError("Invalid or expired session")
            
            # Update last activity
            cursor.execute(
                """
                UPDATE user_sessions 
                SET last_activity = NOW()
                WHERE session_token = %s
                """,
                (session_token,)
            )
            
            return {
                'id': session['id'],
                'email': session['email'],
                'full_name': session['full_name']
            }
    
    def logout(self, session_token: str) -> bool:
        """Invalidate session"""
        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_sessions WHERE session_token = %s",
                (session_token,)
            )
            return True
    
    def request_password_reset(self, email: str) -> dict:
        """Generate password reset token"""
        with get_db_cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                raise ValueError("User not found")
            
            # Generate token
            token = self.generate_token()
            expiry_hours = int(os.getenv('RESET_TOKEN_EXPIRY_HOURS', 1))
            expires_at = datetime.now() + timedelta(hours=expiry_hours)
            
            # Store token
            cursor.execute(
                """
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
                """,
                (user['id'], token, expires_at)
            )
            
            return {
                'token': token,
                'expires_at': expires_at.isoformat()
            }
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        with get_db_cursor() as cursor:
            # Verify token
            cursor.execute(
                """
                SELECT user_id, expires_at, used
                FROM password_reset_tokens
                WHERE token = %s
                """,
                (token,)
            )
            
            reset_token = cursor.fetchone()
            
            if not reset_token:
                raise ValueError("Invalid token")
            
            if reset_token['used']:
                raise ValueError("Token already used")
            
            if datetime.now() > reset_token['expires_at']:
                raise ValueError("Token expired")
            
            # Hash new password
            password_hash = self.hash_password(new_password)
            
            # Update password
            cursor.execute(
                """
                UPDATE users 
                SET password_hash = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (password_hash, reset_token['user_id'])
            )
            
            # Mark token as used
            cursor.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
                (token,)
            )
            
            # Invalidate all sessions for this user
            cursor.execute(
                "DELETE FROM user_sessions WHERE user_id = %s",
                (reset_token['user_id'],)
            )
            
            return True

auth_service = AuthService()