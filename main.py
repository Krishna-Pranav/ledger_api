from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from exceptions import NotFoundError, ConflictError
from routers.accounts import router as accounts_router

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


app.include_router(accounts_router)