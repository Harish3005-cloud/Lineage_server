from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.project_member import ProjectRole, MembershipStatus
from app.schemas.project_member import MemberUserInfo

class ApplicationCreate(BaseModel):
    project_id: UUID = Field(..., description="Target project ID")
    role: Optional[ProjectRole] = Field(None, description="Requested project role")
    statement: Optional[str] = Field(None, max_length=1000, description="Application statement or motivation")

class ApplicationResponse(BaseModel):
    project_member_id: UUID = Field(..., description="Membership record ID representing this application")
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    status: MembershipStatus = Field(default=MembershipStatus.APPLIED, description="Membership status (APPLIED)")
    created_at: datetime
    updated_at: datetime
    user: Optional[MemberUserInfo] = None

    model_config = ConfigDict(from_attributes=True)

class ApplicationListResponse(BaseModel):
    items: List[ApplicationResponse] = Field(default_factory=list, description="List of applications")
    total: int = Field(..., ge=0, description="Total count of applications")

    model_config = ConfigDict(from_attributes=True)
