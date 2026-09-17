from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
from schemas import UserCreate, UserUpdate
from exceptions import NotFoundError, ConflictError
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str
    ) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_user(db: Session, user_in: UserCreate) -> models.User:
    db_user = models.User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )

    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            f"User for email '{user_in.email}' already exists."
        )

    db.refresh(db_user)
    return db_user


def get_user(db: Session, id: int) -> models.User:
    user = db.get(models.User, id)
    if not user:
        raise NotFoundError(f"User with ID {id} doesn't exist.")
    return user


def list_users(db: Session) -> list[models.User]:
    statement = select(models.User)
    return list(db.scalars(statement).all())


def update_user(db: Session, id: int, user_update: UserUpdate) -> models.User:
    user = get_user(db, id)  # raises NotFoundError if missing

    if not verify_password(user_update.old_password, user.password_hash):
        raise ConflictError("Old password is incorrect.")
    if user_update.new_password != user_update.reenter_password:
        raise ConflictError("New password and re-entered password do not match.")

    user.password_hash = hash_password(user_update.new_password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, id: int) -> None:
    user = get_user(db, id)  # raises NotFoundError if missing
    db.delete(user)
    db.commit()
