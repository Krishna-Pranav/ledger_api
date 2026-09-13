from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

class AccountCreate(BaseModel):
    owner_name: str
    currency: str = Field(min_length=3, max_length=3)
    notes: str | None = Field(default=None, max_length=200)

class AccountRead(BaseModel):
    id: int
    owner_name: str
    currency: str
    balance: Decimal
    created_at: datetime
    notes: str | None

    model_config = ConfigDict(from_attributes=True)

class AccountUpdate(BaseModel):
    owner_name: str | None = None
    balance: Decimal = Field(default=Decimal("0.0000"), max_digits=19, decimal_places=4)