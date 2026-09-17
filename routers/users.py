from fastapi import APIRouter, status, Depends, Response
from schemas import UserCreate, UserRead, UserUpdate
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from services import users as user_service


router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(userIn: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, userIn)


@router.get("/{id}", response_model=UserRead)
async def get_user(id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db, id)


@router.get("", response_model=List[UserRead])
async def list_user(db: Session = Depends(get_db)):
    return user_service.list_users(db)


@router.patch("/{id}", response_model=UserRead)
async def patch_user(id: int, account_update: UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db, id, account_update)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: Session = Depends(get_db)):
    user_service.delete_user(db, id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
