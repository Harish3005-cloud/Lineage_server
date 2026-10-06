from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.db.models.project_member import ProjectRole, MembershipStatus

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: Optional[str] = Field(None, description="Project description")

class ProjectResponse(BaseModel):
    project_id: UUID
    title: str
    description: Optional[str] = None
    sponsor_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberApply(BaseModel):
    role: Optional[ProjectRole] = Field(None, description="Requested project role, defaults to mapped platform role")

class ProjectMemberInvite(BaseModel):
    user_id: UUID = Field(..., description="Target user ID to invite")
    role: Optional[ProjectRole] = Field(ProjectRole.STUDENT, description="Role inside project")

class MemberUserInfo(BaseModel):
    user_id: UUID
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberResponse(BaseModel):
    project_member_id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    status: MembershipStatus
    joined_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user: Optional[MemberUserInfo] = None

    model_config = ConfigDict(from_attributes=True)
