from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, func, UniqueConstraint, CheckConstraint, ForeignKey
from sqlalchemy import JSON

class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("owner_name", "currency", name="uq_accounts_owner_currency"),
        CheckConstraint("balance >= 0", name="check_balance_non_negative"),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(30))
    currency: Mapped[str] = mapped_column(String(3))
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4), server_default="0")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    notes: Mapped[str | None] = mapped_column(String(200), nullable=True)

    def __repr__(self) -> str:
        return f"Account(id={self.id!r})"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'", name="check_valid_email"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"


class Transfer(Base):
    __tablename__ = "transfers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    to_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"Transfer(id={self.id!r})"


class Idempotency(Base):
    __tablename__ = "idempotency"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_userid_key"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    key: Mapped[str] = mapped_column(String)
    response_body: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())