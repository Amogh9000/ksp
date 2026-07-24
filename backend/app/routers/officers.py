from fastapi import APIRouter, Depends, Request
from app.models.officer import Officer
from app.schemas.officer import OfficerPublic
from app.core.dependencies import get_current_active_officer
from app.services.audit import log_action
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/officers", tags=["Officers"])


@router.get("/me", response_model=OfficerPublic)
async def get_me(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_active_officer),
):
    await log_action(
        db,
        action="READ_SELF",
        officer_id=current_officer.id,
        resource_type="officer",
        resource_id=str(current_officer.id),
        request=request,
        response_status=200,
    )
    return current_officer
