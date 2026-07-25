"""
criminal_links — the many-to-many table linking criminals to FIRs.
Also encodes the co-accused graph: each row can reference another
CriminalLink row as its "known associate," enabling network analysis.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.base import Base
import enum


class AccusedRole(str, enum.Enum):
    MAIN_ACCUSED = "main_accused"
    CO_ACCUSED = "co_accused"
    ABETTOR = "abettor"
    SUSPECT = "suspect"
    WITNESS = "witness"
    INFORMANT = "informant"


class ArrestStatus(str, enum.Enum):
    NOT_ARRESTED = "not_arrested"
    ARRESTED = "arrested"
    ABSCONDING = "absconding"
    BAILED = "bailed"
    CONVICTED = "convicted"
    ACQUITTED = "acquitted"


class CriminalLink(Base):
    __tablename__ = "criminal_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fir_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("firs.id"), nullable=False
    )
    criminal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("criminals.id"), nullable=False
    )

    role: Mapped[AccusedRole] = mapped_column(
        SAEnum(AccusedRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AccusedRole.SUSPECT,
    )
    arrest_status: Mapped[ArrestStatus] = mapped_column(
        SAEnum(ArrestStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ArrestStatus.NOT_ARRESTED,
    )
    arrest_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Free-text notes (e.g., "drove getaway vehicle")
    role_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Self-referential association: who is this person known to associate with?
    # Stored as a JSON-serialisable list of criminal_link UUIDs on the same FIR.
    # Kept simple (text) to avoid a recursive FK; Track 4 graph work will build on this.
    known_associates_ids: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    fir: Mapped["FIR"] = relationship("FIR", back_populates="accused")
    criminal: Mapped["Criminal"] = relationship("Criminal", back_populates="fir_appearances")
