import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common import PaginationMeta

class ProjectStatus(str, enum.Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    public_summary: Optional[str] = Field(None, description="Public summary of project")
    confidential_brief: Optional[str] = Field(None, description="Confidential brief for accepted members")
    description: Optional[str] = Field(None, description="General or legacy project description")
    status: Optional[ProjectStatus] = Field(default=ProjectStatus.ACTIVE, description="Project status")
    budget: Optional[float] = Field(None, ge=0.0, description="Project budget")

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated project title")
    public_summary: Optional[str] = Field(None, description="Updated public summary")
    confidential_brief: Optional[str] = Field(None, description="Updated confidential brief")
    description: Optional[str] = Field(None, description="Updated general description")
    status: Optional[ProjectStatus] = Field(None, description="Updated project status")
    budget: Optional[float] = Field(None, ge=0.0, description="Updated project budget")

class ProjectResponse(BaseModel):
    project_id: UUID
    sponsor_id: UUID
    title: str
    public_summary: Optional[str] = None
    confidential_brief: Optional[str] = None
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    budget: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectSummary(BaseModel):
    project_id: UUID
    sponsor_id: UUID
    title: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    budget: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse] = Field(default_factory=list, description="List of projects")
    meta: Optional[PaginationMeta] = Field(None, description="Pagination metadata")
    total: int = Field(..., ge=0, description="Total count of projects")

    model_config = ConfigDict(from_attributes=True)
