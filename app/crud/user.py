"""
User CRUD operations - similar to Django ORM querysets.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID - similar to User.objects.get(id=user_id)"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username - similar to User.objects.get(username=username)"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_username_or_email(db: Session, username: str) -> Optional[User]:
    """Get user by username or email for login"""
    return db.query(User).filter(
        or_(User.username == username, User.email == username)
    ).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create new user - similar to User.objects.create_user()
    """
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user - similar to Django's user.save()"""
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete user - similar to user.delete()"""
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False