import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class DisputeStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"

class Dispute(Base):
    __tablename__ = "disputes"

    dispute_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    contribution_id = Column(UUID(as_uuid=True), ForeignKey("contributions.contribution_id", ondelete="SET NULL"), nullable=True)
    raiser_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(
        SAEnum(DisputeStatus, name="dispute_status_enum", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=DisputeStatus.OPEN,
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
    contribution = relationship("Contribution")
    raiser = relationship("User")
