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

class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)

class UserRead(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)
    reenter_password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str