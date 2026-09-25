from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import models
from exceptions import NotFoundError, ConflictError, ForbiddenError
from schemas import TransferRead


def _get_idempotent_response(db: Session, user_id: int, idempotency_key: str) -> dict | None:
    existing = db.execute(
        select(models.Idempotency).where(
            models.Idempotency.user_id == user_id,
            models.Idempotency.key == idempotency_key,
        )
    ).scalar_one_or_none()
    return existing.response_body if existing else None


def transfer_create(db: Session, from_account_id: int, to_account_id: int, amount: Decimal, user_id: int, idempotency_key: str) -> models.Transfer:
    # lock rows in a consistent (lowest-id-first) order to avoid deadlocks
    if idempotency_key:
        existing_response = _get_idempotent_response(db, user_id, idempotency_key)
        if existing_response:
            return existing_response
    first_id, second_id = sorted([from_account_id, to_account_id])
    first = db.execute(
        select(models.Account).where(models.Account.id == first_id).with_for_update()
    ).scalar_one_or_none()
    second = db.execute(
        select(models.Account).where(models.Account.id == second_id).with_for_update()
    ).scalar_one_or_none()

    from_acc = first if first_id == from_account_id else second
    to_acc = second if second_id == to_account_id else first

    if not from_acc:
        db.rollback()
        raise NotFoundError(f"Account with ID {from_account_id} doesn't exist.")
    if not to_acc:
        db.rollback()
        raise NotFoundError(f"Account with ID {to_account_id} doesn't exist.")
    if from_acc.user_id != user_id:
        db.rollback()
        raise ForbiddenError(f"Account {from_account_id} doesn't belong to you")
    if from_acc.balance < amount:
        db.rollback()
        raise ConflictError("insufficient funds.")

    from_acc.balance -= amount
    to_acc.balance += amount

    db_transfer = models.Transfer(
        from_account_id=from_account_id,
        to_account_id=to_account_id,
        amount=amount,
    )
    db.add(db_transfer)
    db.flush()
    response_data = TransferRead.model_validate(db_transfer).model_dump(mode="json")

    if idempotency_key:
        db.add(models.Idempotency(user_id=user_id, key=idempotency_key, response_body=response_data))
        try:
            db.commit()
        except IntegrityError:
            # another concurrent request won the race and inserted this (user_id, key) first
            db.rollback()
            return _get_idempotent_response(db, user_id, idempotency_key)
    else:
        db.commit()

    db.refresh(db_transfer)
    return db_transfer
