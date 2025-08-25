from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: str
    username: str

class UserCreate(UserBase):
    """Schema for user registration - similar to DRF's create serializer"""
    password: str

class UserUpdate(BaseModel):
    """Schema for user updates"""
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    """
    Schema for user response - similar to DRF's read serializer.
    This is what gets returned in API responses.
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True