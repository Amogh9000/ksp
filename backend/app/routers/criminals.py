from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.database import get_db
from app.models.criminal import Criminal
from app.models.officer import Officer
from app.schemas.criminal import CriminalCreate, CriminalPublic, CriminalListResponse
from app.core.dependencies import (
    get_current_active_officer,
    require_supervisor_or_above,
)
from app.services.audit import log_action

router = APIRouter(prefix="/criminals", tags=["Criminals"])


@router.get("", response_model=CriminalListResponse)
async def list_criminals(
    request: Request,
    name: str | None = Query(None),
    district: str | None = Query(None),
    is_wanted: bool | None = Query(None),
    is_repeat_offender: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_active_officer),
):
    query = select(Criminal)

    if name:
        query = query.where(
            or_(
                Criminal.full_name.ilike(f"%{name}%"),
                Criminal.alias.ilike(f"%{name}%"),
            )
        )
    if district:
        query = query.where(Criminal.district == district)
    if is_wanted is not None:
        query = query.where(Criminal.is_wanted == is_wanted)
    if is_repeat_offender is not None:
        query = query.where(Criminal.is_repeat_offender == is_repeat_offender)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    criminals = result.scalars().all()

    await log_action(
        db,
        action="LIST_CRIMINALS",
        officer_id=current_officer.id,
        resource_type="criminal",
        request=request,
        request_summary={"name": name, "district": district, "page": page},
        response_status=200,
    )

    return CriminalListResponse(
        total=total, page=page, page_size=page_size, items=criminals
    )


@router.get("/{criminal_id}", response_model=CriminalPublic)
async def get_criminal(
    criminal_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_active_officer),
):
    result = await db.execute(select(Criminal).where(Criminal.id == criminal_id))
    criminal = result.scalar_one_or_none()
    if not criminal:
        raise HTTPException(status_code=404, detail="Criminal record not found.")

    await log_action(
        db,
        action="READ_CRIMINAL",
        officer_id=current_officer.id,
        resource_type="criminal",
        resource_id=str(criminal_id),
        request=request,
        response_status=200,
    )
    return criminal


@router.post("", response_model=CriminalPublic, status_code=status.HTTP_201_CREATED)
async def create_criminal(
    body: CriminalCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(require_supervisor_or_above()),
):
    criminal = Criminal(**body.model_dump())
    db.add(criminal)
    await db.flush()

    await log_action(
        db,
        action="CREATE_CRIMINAL",
        officer_id=current_officer.id,
        resource_type="criminal",
        resource_id=str(criminal.id),
        request=request,
        response_status=201,
    )
    return criminal
