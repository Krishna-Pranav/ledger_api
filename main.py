from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from exceptions import NotFoundError, ConflictError, UnauthorizedError, ForbiddenError
from routers.accounts import router as accounts_router
from routers.users import router as users_router
from routers.auth import router as auth_router

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


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=error_body("UNAUTHORIZED", exc.message))


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=error_body("FORBIDDEN", exc.message))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(accounts_router)
app.include_router(users_router)
app.include_router(auth_router)