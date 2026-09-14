from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
from schemas import AccountCreate, AccountUpdate
from exceptions import NotFoundError, ConflictError


def create_account(db: Session, account_in: AccountCreate) -> models.Account:
    db_account = models.Account(**account_in.model_dump())

    db.add(db_account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            f"Account for owner '{account_in.owner_name}' in {account_in.currency} already exists."
        )

    db.refresh(db_account)
    return db_account


def get_account(db: Session, id: int) -> models.Account:
    account = db.get(models.Account, id)
    if not account:
        raise NotFoundError(f"Account with ID {id} doesn't exist.")
    return account


def list_accounts(db: Session) -> list[models.Account]:
    statement = select(models.Account)
    return list(db.scalars(statement).all())


def update_account(db: Session, id: int, account_update: AccountUpdate) -> models.Account:
    account = get_account(db, id)  # raises NotFoundError if missing

    update_data = account_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, id: int) -> None:
    account = get_account(db, id)  # raises NotFoundError if missing
    db.delete(account)
    db.commit()
