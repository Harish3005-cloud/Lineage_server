import enum
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class LedgerActionType(str, enum.Enum):
    PROJECT_INITIALIZED = "PROJECT_INITIALIZED"
    CHARTER_RATIFIED = "CHARTER_RATIFIED"
    CONTRIBUTION_RECORDED = "CONTRIBUTION_RECORDED"
    REVIEW_FINALIZED = "REVIEW_FINALIZED"
    ESCROW_FUNDED = "ESCROW_FUNDED"
    PAYOUT_EXECUTED = "PAYOUT_EXECUTED"
    DISPUTE_LOGGED = "DISPUTE_LOGGED"
    DISPUTE_RESOLVED = "DISPUTE_RESOLVED"
    ADMIN_AUDIT = "ADMIN_AUDIT"

class LedgerEntryCreate(BaseModel):
    project_id: UUID = Field(..., description="Project ID associated with ledger entry")
    contribution_id: Optional[UUID] = Field(None, description="Optional contribution ID")
    admin_id: UUID = Field(..., description="Administrator user ID performing or sealing the action (NO actor_id)")
    action_type: LedgerActionType = Field(..., description="Action classification")
    payload: Optional[Any] = Field(None, description="Arbitrary audit payload/data")
    previous_hash: str = Field(..., min_length=1, max_length=128, description="Cryptographic hash of the previous ledger entry")
    current_hash: str = Field(..., min_length=1, max_length=128, description="Cryptographic hash of the current ledger entry")

class LedgerEntryResponse(BaseModel):
    ledger_entry_id: UUID
    project_id: UUID
    contribution_id: Optional[UUID] = None
    admin_id: UUID
    action_type: LedgerActionType
    payload: Optional[Any] = None
    previous_hash: str
    current_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LedgerEntryListResponse(BaseModel):
    items: List[LedgerEntryResponse] = Field(default_factory=list, description="List of ledger entries")
    total: int = Field(..., ge=0, description="Total count of ledger entries")

    model_config = ConfigDict(from_attributes=True)
