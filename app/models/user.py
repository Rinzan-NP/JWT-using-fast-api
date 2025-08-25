from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid

class UserRole(Enum):
    ADMIN = "admin"
    DRIVER = "driver"
    SHIPPER = "shipper"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    role = Column(
        SQLEnum(UserRole, name="user_roles", native_enum=False), 
        default=UserRole.SHIPPER,
        nullable=False
    )

    # Relationships
    items = relationship("Item", back_populates="owner")
