import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class IntegrityStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SUSPICIOUS = "SUSPICIOUS"
    FLAGGED = "FLAGGED"

class ReviewDecision(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    REJECTED = "REJECTED"

class ReviewCreate(BaseModel):
    contribution_id: UUID = Field(..., description="Contribution ID under review")
    reviewer_id: UUID = Field(..., description="Reviewer user ID")
    impact_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Impact score (0 to 100)")
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Similarity score (0.0 to 1.0)")
    integrity_status: Optional[IntegrityStatus] = Field(default=IntegrityStatus.PENDING, description="Integrity status")
    decision: Optional[ReviewDecision] = Field(default=ReviewDecision.PENDING, description="Review decision")
    comments: Optional[str] = Field(None, description="Review feedback/comments")

class ReviewUpdate(BaseModel):
    impact_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Updated impact score")
    similarity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Updated similarity score")
    integrity_status: Optional[IntegrityStatus] = Field(None, description="Updated integrity status")
    decision: Optional[ReviewDecision] = Field(None, description="Updated decision")
    comments: Optional[str] = Field(None, description="Updated comments")

class ReviewResponse(BaseModel):
    review_id: UUID
    contribution_id: UUID
    reviewer_id: UUID
    impact_score: Optional[float] = None
    similarity_score: Optional[float] = None
    integrity_status: IntegrityStatus
    decision: ReviewDecision
    comments: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReviewListResponse(BaseModel):
    items: List[ReviewResponse] = Field(default_factory=list, description="List of reviews")
    total: int = Field(..., ge=0, description="Total count of reviews")

    model_config = ConfigDict(from_attributes=True)
