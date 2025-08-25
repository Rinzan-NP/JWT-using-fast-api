from pydantic import BaseModel
from typing import Optional

class TokenPair(BaseModel):
    """
    Token pair response - similar to SimpleJWT's token pair.
    Contains both access and refresh tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    """Login request schema"""
    username: str  # Can be username or email
    password: str

class RefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str