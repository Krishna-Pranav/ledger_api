from decimal import Decimal
from fastapi import APIRouter, Depends, Response, status, Header
from sqlalchemy.orm import Session
from database import get_db
from schemas import TransferRead
from services import transfers as transfers_service
from dependencies import get_current_user
import models

router = APIRouter(prefix="/transfers", tags=["transfers"])

@router.post("", response_model=TransferRead, status_code=status.HTTP_200_OK)
def create_transfer(from_account: int, to_account: int, amount: Decimal, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return transfers_service.transfer_create(db, from_account, to_account, amount, current_user.id, idempotency_key)