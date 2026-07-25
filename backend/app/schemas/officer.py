import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.officer import OfficerRank, OfficerRole


class OfficerPublic(BaseModel):
    id: uuid.UUID
    badge_number: str
    full_name: str
    email: EmailStr
    rank: OfficerRank
    role: OfficerRole
    station_id: uuid.UUID | None
    jurisdiction_district: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
