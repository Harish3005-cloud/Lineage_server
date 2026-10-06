import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Numeric, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class PayoutStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Payout(Base):
    __tablename__ = "payouts"

    payout_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    escrow_id = Column(UUID(as_uuid=True), ForeignKey("escrows.escrow_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SAEnum(PayoutStatus, name="payout_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=PayoutStatus.PENDING,
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    escrow = relationship("Escrow")
    user = relationship("User")
