"""
Authentication routes - similar to DRF's authentication views.
Handles signup, login, token refresh, and logout.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from app.crud.user import (
    create_user, 
    get_user_by_username_or_email,
    get_user_by_username
)
from app.crud.auth import (
    create_refresh_token as store_refresh_token,
    is_token_valid,
    delete_refresh_token,
    delete_user_refresh_tokens
)
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.auth import (
    TokenPair, 
    LoginRequest, 
    RefreshRequest,
    MessageResponse
)
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    User registration endpoint.
   
    """
   
    
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    user = create_user(db, user_data)
    return user

@router.post("/login", response_model=TokenPair)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login endpoint.
    Similar to SimpleJWT's TokenObtainPairView.
    Returns both access and refresh tokens.
    """
    # Authenticate user
    user = get_user_by_username_or_email(db, login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in database
    store_refresh_token(db, refresh_token, user.id)
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenPair)
def refresh_token(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Token refresh endpoint.
    Similar to SimpleJWT's TokenRefreshView.
    Generates new access token using valid refresh token.
    """
    # Verify refresh token format
    payload = verify_token(refresh_data.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if refresh token exists in database (not revoked)
    if not is_token_valid(db, refresh_data.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired"
        )
    
    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Create new token pair
    access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Replace old refresh token with new one
    delete_refresh_token(db, refresh_data.refresh_token)
    store_refresh_token(db, new_refresh_token, int(user_id))
    
    return TokenPair(
        access_token=access_token,
        refresh_token=new_refresh_token
    )

@router.post("/logout", response_model=MessageResponse)
def logout(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Logout endpoint.
    Similar to SimpleJWT's logout by blacklisting the refresh token.
    Revokes refresh token by removing it from database.
    """
    # Delete/revoke the refresh token
    success = delete_refresh_token(db, refresh_data.refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    return MessageResponse(message="Successfully logged out")

@router.post("/logout-all", response_model=MessageResponse)
def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout from all devices.
    Revokes all refresh tokens for the current user.
    """
    deleted_count = delete_user_refresh_tokens(db, current_user.id)
    
    return MessageResponse(
        message=f"Successfully logged out from {deleted_count} devices"
    )