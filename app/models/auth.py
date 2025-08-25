"""
RefreshToken model for token blacklist/revocation.
Similar to SimpleJWT's blacklisted tokens but we store valid tokens instead.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="refresh_tokens")