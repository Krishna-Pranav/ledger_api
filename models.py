from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, Numeric, func, UniqueConstraint, CheckConstraint

class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("owner_name", "currency", name="uq_accounts_owner_currency"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
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
