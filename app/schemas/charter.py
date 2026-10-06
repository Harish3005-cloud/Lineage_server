import enum
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class CharterStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    REVISED = "REVISED"
    ARCHIVED = "ARCHIVED"

class CharterCreate(BaseModel):
    project_id: UUID = Field(..., description="Target project ID")
    version: str = Field(default="1.0", min_length=1, max_length=50, description="Charter version")
    scope: str = Field(..., min_length=1, description="Charter scope")
    roles: Optional[Any] = Field(None, description="Roles definition/mapping")
    reward_terms: Optional[str] = Field(None, description="Reward terms")
    acceptance_criteria: Optional[str] = Field(None, description="Acceptance criteria")
    ip_terms: Optional[str] = Field(None, description="Intellectual property terms")
    status: Optional[CharterStatus] = Field(default=CharterStatus.DRAFT, description="Charter status")

class CharterUpdate(BaseModel):
    version: Optional[str] = Field(None, min_length=1, max_length=50, description="Updated version")
    scope: Optional[str] = Field(None, description="Updated scope")
    roles: Optional[Any] = Field(None, description="Updated roles")
    reward_terms: Optional[str] = Field(None, description="Updated reward terms")
    acceptance_criteria: Optional[str] = Field(None, description="Updated acceptance criteria")
    ip_terms: Optional[str] = Field(None, description="Updated IP terms")
    status: Optional[CharterStatus] = Field(None, description="Updated status")

class CharterResponse(BaseModel):
    charter_id: UUID
    project_id: UUID
    version: str
    scope: str
    roles: Optional[Any] = None
    reward_terms: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    ip_terms: Optional[str] = None
    status: CharterStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CharterListResponse(BaseModel):
    items: List[CharterResponse] = Field(default_factory=list, description="List of charters")
    total: int = Field(..., ge=0, description="Total count of charters")

    model_config = ConfigDict(from_attributes=True)
