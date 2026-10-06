from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class WorkspaceCreate(BaseModel):
    project_id: UUID = Field(..., description="Project ID this workspace belongs to")
    name: str = Field(..., min_length=1, max_length=255, description="Workspace name")
    description: Optional[str] = Field(None, description="Workspace description")

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated workspace name")
    description: Optional[str] = Field(None, description="Updated workspace description")

class WorkspaceResponse(BaseModel):
    workspace_id: UUID
    project_id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkspaceSummary(BaseModel):
    workspace_id: UUID
    project_id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

class WorkspaceListResponse(BaseModel):
    items: List[WorkspaceResponse] = Field(default_factory=list, description="List of workspaces")
    total: int = Field(..., ge=0, description="Total workspace count")

    model_config = ConfigDict(from_attributes=True)
