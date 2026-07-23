from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.officer import Officer, OfficerRank, OfficerRole
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, RefreshRequest
from app.schemas.officer import OfficerPublic
from app.services.audit import log_action

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=OfficerPublic, status_code=status.HTTP_201_CREATED)
async def signup(
    body: SignupRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Check uniqueness
    existing = await db.execute(
        select(Officer).where(
            (Officer.email == body.email) | (Officer.badge_number == body.badge_number)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An officer with this email or badge number already exists.",
        )

    try:
        rank = OfficerRank(body.rank)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid rank: {body.rank}")

    officer = Officer(
        badge_number=body.badge_number,
        full_name=body.full_name,
        email=body.email,
        hashed_password=hash_password(body.password),
        rank=rank,
        role=OfficerRole.OFFICER,  # new signups are always basic officers
    )
    db.add(officer)
    await db.flush()  # get the ID before audit log

    await log_action(
        db,
        action="SIGNUP",
        officer_id=officer.id,
        resource_type="officer",
        resource_id=str(officer.id),
        request=request,
        response_status=201,
    )
    return officer


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Officer).where(Officer.email == body.email))
    officer = result.scalar_one_or_none()

    if not officer or not verify_password(body.password, officer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if not officer.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    # Update last login timestamp
    officer.last_login = datetime.now(tz=timezone.utc)

    await log_action(
        db,
        action="LOGIN",
        officer_id=officer.id,
        resource_type="officer",
        resource_id=str(officer.id),
        request=request,
        response_status=200,
    )

    return TokenResponse(
        access_token=create_access_token(str(officer.id)),
        refresh_token=create_refresh_token(str(officer.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
    )
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise credentials_exc
        officer_id: str = payload.get("sub")
    except JWTError:
        raise credentials_exc

    result = await db.execute(
        select(Officer).where(Officer.id == officer_id)
    )
    officer = result.scalar_one_or_none()
    if not officer or not officer.is_active:
        raise credentials_exc

    await log_action(
        db,
        action="TOKEN_REFRESH",
        officer_id=officer.id,
        request=request,
        response_status=200,
    )

    return TokenResponse(
        access_token=create_access_token(str(officer.id)),
        refresh_token=create_refresh_token(str(officer.id)),
    )
