"""
audit_logs — every read and write through the API is recorded here.
Immutable by design: no update/delete routes will be exposed for this table.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    officer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("officers.id"), nullable=True
    )
    # Fallback for unauthenticated or system events
    actor_label: Mapped[str] = mapped_column(String(200), nullable=True)

    action: Mapped[str] = mapped_column(String(100), nullable=False)   # e.g. "READ_FIR"
    resource_type: Mapped[str] = mapped_column(String(100), nullable=True)  # "fir"
    resource_id: Mapped[str] = mapped_column(String(200), nullable=True)    # UUID of record

    # HTTP context
    http_method: Mapped[str] = mapped_column(String(10), nullable=True)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)

    # Query params / request body summary (PII-scrubbed before storage)
    request_summary: Mapped[dict] = mapped_column(JSONB, nullable=True)
    response_status: Mapped[int] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationship
    officer: Mapped["Officer"] = relationship("Officer", back_populates="audit_logs")
