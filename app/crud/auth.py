from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from app.models.auth import RefreshToken
from app.models.user import User
from app.core.config import settings

def create_refresh_token(db: Session, token: str, user_id: int) -> RefreshToken:
    """
    Store refresh token in database.
    
    """
    expires_at = datetime.now() + timedelta(days=settings.refresh_token_expire_days)
    
    db_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """
    Get refresh token from database.
    Used to check if token exists and is not revoked.
    """
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()

def is_token_valid(db: Session, token: str) -> bool:
    """
    Check if refresh token is valid (exists in DB and not expired).
    Similar to SimpleJWT's blacklist checking but reversed logic.
    """
    db_token = get_refresh_token(db, token)
    if not db_token:
        return False
    
    # Check if token is expired
    if db_token.expires_at < datetime.utcnow():
        # Clean up expired token
        delete_refresh_token(db, token)
        return False
    
    return True

def delete_refresh_token(db: Session, token: str) -> bool:
    """
    Delete/revoke refresh token.
    Similar to SimpleJWT's token blacklisting on logout.
    """
    db_token = get_refresh_token(db, token)
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    return False

def delete_user_refresh_tokens(db: Session, user_id: int) -> int:
    """
    Delete all refresh tokens for a user.
    Useful for "logout from all devices" functionality.
    """
    deleted_count = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
    db.commit()
    return deleted_count

def cleanup_expired_tokens(db: Session) -> int:
    """
    Clean up expired refresh tokens.
    Should be run periodically (e.g., with a cron job).
    """
    deleted_count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return deleted_count