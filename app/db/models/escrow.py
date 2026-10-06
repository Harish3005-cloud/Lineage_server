import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class EscrowStatus(str, enum.Enum):
    PENDING = "PENDING"
    FUNDED = "FUNDED"
    RELEASED = "RELEASED"
    REFUNDED = "REFUNDED"

class Escrow(Base):
    __tablename__ = "escrows"

    escrow_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    status = Column(
        SAEnum(EscrowStatus, name="escrow_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=EscrowStatus.PENDING,
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project = relationship("Project")
