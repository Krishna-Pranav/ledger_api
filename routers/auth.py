from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserLogin, TokenPair, RefreshRequest
from services import users as user_service
from security import create_access_token, create_refresh_token, decode_token
from exceptions import UnauthorizedError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, credentials.email, credentials.password)
    return TokenPair(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Token is not a refresh token.")

    subject = payload["sub"]
    return TokenPair(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )
