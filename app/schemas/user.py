from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.db.models.user import UserRole, VerificationStatus

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name of user")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=6, max_length=128, description="User password")
    age: int = Field(..., ge=0, le=150, description="User age")
    role: UserRole = Field(..., description="Role: STUDENT, EXPERT, or SPONSOR")
    skills: Optional[Any] = Field(default_factory=list, description="List of skills or details")
    availability: Optional[str] = Field(default=None, max_length=255, description="Availability description")

    @field_validator("role")
    @classmethod
    def validate_public_registration_role(cls, v: UserRole) -> UserRole:
        if v == UserRole.ADMIN:
            raise ValueError("Public registration cannot assign the ADMIN role")
        return v

class UserResponse(BaseModel):
    user_id: UUID
    name: str
    email: EmailStr
    age: int
    is_under_18: bool
    role: UserRole
    skills: Optional[Any] = None
    availability: Optional[str] = None
    verification_status: VerificationStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
