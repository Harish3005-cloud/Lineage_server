import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class DisputeStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class DisputeCreate(BaseModel):
    project_id: UUID = Field(..., description="Project ID associated with dispute")
    raised_by: UUID = Field(..., description="User ID who raised the dispute")
    contribution_id: Optional[UUID] = Field(None, description="Optional contribution ID under dispute")
    reason: str = Field(..., min_length=1, description="Reason for the dispute")
    status: Optional[DisputeStatus] = Field(default=DisputeStatus.OPEN, description="Dispute status")

class DisputeUpdate(BaseModel):
    status: Optional[DisputeStatus] = Field(None, description="Updated dispute status")
    resolved_by: Optional[UUID] = Field(None, description="User ID who resolved/dismissed dispute")
    resolution: Optional[str] = Field(None, description="Resolution statement or notes")
    resolved_at: Optional[datetime] = Field(None, description="Timestamp when resolved")

class DisputeResponse(BaseModel):
    dispute_id: UUID
    project_id: UUID
    raised_by: UUID
    contribution_id: Optional[UUID] = None
    resolved_by: Optional[UUID] = None
    reason: str
    status: DisputeStatus
    resolution: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class DisputeListResponse(BaseModel):
    items: List[DisputeResponse] = Field(default_factory=list, description="List of disputes")
    total: int = Field(..., ge=0, description="Total count of disputes")

    model_config = ConfigDict(from_attributes=True)
