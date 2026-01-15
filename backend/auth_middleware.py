from fastapi import HTTPException, Header
from typing import Optional
from backend.auth_service import auth_service

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current user from session token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        user = auth_service.verify_session(token)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_optional_user(authorization: Optional[str] = Header(None)):
    """Optional authentication - returns user if authenticated, None otherwise"""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            return None
        user = auth_service.verify_session(token)
        return user
    except (ValueError, Exception):
        return None