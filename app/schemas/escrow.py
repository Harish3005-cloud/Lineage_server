import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class EscrowStatus(str, enum.Enum):
    PENDING = "PENDING"
    FUNDED = "FUNDED"
    LOCKED = "LOCKED"
    RELEASED = "RELEASED"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"

class EscrowCreate(BaseModel):
    project_id: UUID = Field(..., description="Project ID")
    milestone_id: Optional[UUID] = Field(None, description="Optional milestone ID")
    amount: float = Field(..., ge=0.0, description="Escrow funding amount")
    status: Optional[EscrowStatus] = Field(default=EscrowStatus.PENDING, description="Escrow status")
    funded_at: Optional[datetime] = Field(None, description="Timestamp when funded")

class EscrowUpdate(BaseModel):
    amount: Optional[float] = Field(None, ge=0.0, description="Updated amount")
    status: Optional[EscrowStatus] = Field(None, description="Updated escrow status")
    funded_at: Optional[datetime] = Field(None, description="Timestamp funded")
    released_at: Optional[datetime] = Field(None, description="Timestamp released")

class EscrowResponse(BaseModel):
    escrow_id: UUID
    project_id: UUID
    milestone_id: Optional[UUID] = None
    amount: float
    status: EscrowStatus
    funded_at: Optional[datetime] = None
    released_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EscrowListResponse(BaseModel):
    items: List[EscrowResponse] = Field(default_factory=list, description="List of escrows")
    total: int = Field(..., ge=0, description="Total count of escrows")

    model_config = ConfigDict(from_attributes=True)
