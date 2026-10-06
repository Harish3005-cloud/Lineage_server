import enum
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class MilestoneStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    CANCELLED = "CANCELLED"

class MilestoneCreate(BaseModel):
    project_id: UUID = Field(..., description="Target project ID")
    title: str = Field(..., min_length=1, max_length=255, description="Milestone title")
    description: Optional[str] = Field(None, description="Milestone description")
    required_skills: Optional[Any] = Field(None, description="Required skills list/JSON")
    acceptance_criteria: Optional[str] = Field(None, description="Acceptance criteria")
    reward_amount: float = Field(default=0.0, ge=0.0, description="Reward amount for completing milestone")
    status: Optional[MilestoneStatus] = Field(default=MilestoneStatus.PENDING, description="Milestone status")

class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    required_skills: Optional[Any] = Field(None, description="Updated required skills")
    acceptance_criteria: Optional[str] = Field(None, description="Updated acceptance criteria")
    reward_amount: Optional[float] = Field(None, ge=0.0, description="Updated reward amount")
    status: Optional[MilestoneStatus] = Field(None, description="Updated status")

class MilestoneResponse(BaseModel):
    milestone_id: UUID
    project_id: UUID
    title: str
    description: Optional[str] = None
    required_skills: Optional[Any] = None
    acceptance_criteria: Optional[str] = None
    reward_amount: float
    status: MilestoneStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MilestoneListResponse(BaseModel):
    items: List[MilestoneResponse] = Field(default_factory=list, description="List of milestones")
    total: int = Field(..., ge=0, description="Total count of milestones")

    model_config = ConfigDict(from_attributes=True)
