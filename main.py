from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from schemas import AccountCreate, AccountRead, AccountUpdate
from exceptions import NotFoundError, ConflictError
import models
from typing import List

app = FastAPI()


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=error_body("NOT_FOUND", exc.message))


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=error_body("CONFLICT", exc.message))


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=error_body("VALIDATION_ERROR", str(exc.errors())))


@app.get("/health")
async def health_check():
    return {"status": "ok"}

# @app.get("/db-check")
# def db_check(db: Session = Depends(get_db)):
#     result = db.execute(text("SELECT 1")).scalar()
#     return {"db_says": result}

@app.post("/accounts", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(account_in: AccountCreate, db: Session = Depends(get_db)):
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


@app.get("/accounts/{id}", response_model=AccountRead)
async def get_account(id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == id).first()
    if not account:
        raise NotFoundError(f"Account with ID {id} doesn't exist.")
    return account


@app.get("/accounts", response_model=List[AccountRead])
async def get_accounts(db: Session = Depends(get_db)):
    statement = select(models.Account)
    accounts = db.scalars(statement).all()
    return accounts


@app.patch("/accounts/{id}", response_model=AccountRead, status_code=status.HTTP_200_OK)
async def patch_account(account_update: AccountUpdate, id: int, db: Session = Depends(get_db)):
    account = db.get(models.Account, id)
    if not account:
        raise NotFoundError(f"Account with ID {id} doesn't exist.")

    update_data = account_update.model_dump(exclude_unset=True)
    for f, v in update_data.items():
        setattr(account, f, v)
    db.commit()
    db.refresh(account)
    return account


@app.delete("/accounts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(id: int, db: Session = Depends(get_db)):
    account = db.get(models.Account, id)
    if not account:
        raise NotFoundError(f"Account with ID {id} doesn't exist.")
    db.delete(account)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)