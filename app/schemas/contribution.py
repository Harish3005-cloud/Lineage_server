import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class ContributionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class ContributionCreate(BaseModel):
    project_id: UUID = Field(..., description="Target project ID")
    milestone_id: Optional[UUID] = Field(None, description="Optional milestone ID")
    user_id: UUID = Field(..., description="Contributor user ID")
    human_owner_id: Optional[UUID] = Field(None, description="Human owner user ID (for accountability/attribution)")
    artifact_name: str = Field(..., min_length=1, max_length=255, description="Name of the contributed artifact")
    artifact_hash: str = Field(..., min_length=1, max_length=128, description="Cryptographic hash of the artifact content")
    parent_hash: Optional[str] = Field(None, max_length=128, description="Parent artifact hash for lineage tracking")
    origin: Optional[str] = Field(None, max_length=100, description="Artifact origin (e.g. HUMAN, COLLAB, REPOSITORY)")
    ai_assisted: bool = Field(default=False, description="Whether the contribution was AI-assisted")
    status: Optional[ContributionStatus] = Field(default=ContributionStatus.SUBMITTED, description="Contribution status")

class ContributionUpdate(BaseModel):
    artifact_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated artifact name")
    artifact_hash: Optional[str] = Field(None, max_length=128, description="Updated artifact hash")
    parent_hash: Optional[str] = Field(None, max_length=128, description="Updated parent hash")
    origin: Optional[str] = Field(None, max_length=100, description="Updated origin")
    ai_assisted: Optional[bool] = Field(None, description="Updated AI assistance flag")
    status: Optional[ContributionStatus] = Field(None, description="Updated contribution status")

class ContributionResponse(BaseModel):
    contribution_id: UUID
    project_id: UUID
    milestone_id: Optional[UUID] = None
    user_id: UUID
    human_owner_id: Optional[UUID] = None
    artifact_name: str
    artifact_hash: str
    parent_hash: Optional[str] = None
    origin: Optional[str] = None
    ai_assisted: bool = False
    status: ContributionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ContributionListResponse(BaseModel):
    items: List[ContributionResponse] = Field(default_factory=list, description="List of contributions")
    total: int = Field(..., ge=0, description="Total count of contributions")

    model_config = ConfigDict(from_attributes=True)
