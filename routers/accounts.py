from typing import List

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import AccountCreate, AccountRead, AccountUpdate
from services import accounts as accounts_service
from dependencies import get_current_user
import models

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(account_in: AccountCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return accounts_service.create_account(db, account_in, current_user.id)


@router.get("/{id}", response_model=AccountRead)
async def get_account(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return accounts_service.get_account(db, id, current_user.id)


@router.get("", response_model=List[AccountRead])
async def list_accounts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return accounts_service.list_accounts(db, current_user.id)


@router.patch("/{id}", response_model=AccountRead)
async def patch_account(id: int, account_update: AccountUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return accounts_service.update_account(db, id, account_update, current_user.id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    accounts_service.delete_account(db, id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
