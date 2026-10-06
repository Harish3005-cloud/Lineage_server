import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class PayoutStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"

class PayoutCreate(BaseModel):
    escrow_id: UUID = Field(..., description="Escrow record ID from which funds originate")
    user_id: UUID = Field(..., description="Recipient user ID")
    contribution_id: Optional[UUID] = Field(None, description="Optional contribution ID triggering payout")
    amount: float = Field(..., ge=0.0, description="Payout amount")
    reason: Optional[str] = Field(None, description="Reason for payout")
    status: Optional[PayoutStatus] = Field(default=PayoutStatus.PENDING, description="Payout status")

class PayoutUpdate(BaseModel):
    status: Optional[PayoutStatus] = Field(None, description="Updated payout status")
    reason: Optional[str] = Field(None, description="Updated reason")

class PayoutResponse(BaseModel):
    payout_id: UUID
    escrow_id: UUID
    user_id: UUID
    contribution_id: Optional[UUID] = None
    amount: float
    reason: Optional[str] = None
    status: PayoutStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PayoutListResponse(BaseModel):
    items: List[PayoutResponse] = Field(default_factory=list, description="List of payouts")
    total: int = Field(..., ge=0, description="Total count of payouts")

    model_config = ConfigDict(from_attributes=True)
