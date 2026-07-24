import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.base import Base
import enum


class OfficerRank(str, enum.Enum):
    CONSTABLE = "constable"
    HEAD_CONSTABLE = "head_constable"
    ASI = "asi"           # Assistant Sub-Inspector
    SI = "si"             # Sub-Inspector
    PSI = "psi"           # Police Sub-Inspector
    PI = "pi"             # Police Inspector
    DySP = "dysp"         # Deputy Superintendent of Police
    SP = "sp"             # Superintendent of Police
    DIG = "dig"           # Deputy Inspector General
    IG = "ig"             # Inspector General
    DGP = "dgp"           # Director General of Police


class OfficerRole(str, enum.Enum):
    OFFICER = "officer"           # Read own jurisdiction
    SUPERVISOR = "supervisor"     # Read/write own district
    ANALYST = "analyst"           # Read all districts
    ADMIN = "admin"               # Full access


class Officer(Base):
    __tablename__ = "officers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    badge_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    rank: Mapped[OfficerRank] = mapped_column(
        SAEnum(OfficerRank, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=OfficerRank.CONSTABLE,
    )
    role: Mapped[OfficerRole] = mapped_column(
        SAEnum(OfficerRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=OfficerRole.OFFICER,
    )

    station_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stations.id"), nullable=True
    )
    # District-level jurisdiction override (for DySP and above)
    jurisdiction_district: Mapped[str] = mapped_column(String(100), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    station: Mapped["Station"] = relationship("Station", back_populates="officers")
    firs_filed: Mapped[list["FIR"]] = relationship(
        "FIR", back_populates="investigating_officer", lazy="selectin"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="officer", lazy="noload"
    )
