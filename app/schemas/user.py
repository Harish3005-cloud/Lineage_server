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

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated full name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Updated age")
    skills: Optional[Any] = Field(None, description="Updated skills list or object")
    availability: Optional[str] = Field(None, max_length=255, description="Updated availability description")

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

class UserProfileResponse(UserResponse):
    pass

class StudentProfileResponse(UserProfileResponse):
    education_level: Optional[str] = None

class ExpertProfileResponse(UserProfileResponse):
    domain_expertise: Optional[str] = None

class SponsorProfileResponse(UserProfileResponse):
    organization_name: Optional[str] = None

class MentorProfileResponse(UserProfileResponse):
    mentorship_focus: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
