from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

from lyceum.auth.exceptions import (
    AccountAlreadyExistsError,
    InvalidCredentialsError,
    MissingAccessTokenError,
)
from lyceum.shared.schemas import ErrorResponse


def register_auth_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AccountAlreadyExistsError)
    async def handle_account_already_exists_error(
        request: Request,
        exception: AccountAlreadyExistsError,
    ) -> JSONResponse:
        if exception.field is not None:
            msg = f"{exception.field} đã tồn tại"
        else:
            msg = "Username hoặc email đã tồn tại"

        body = ErrorResponse(msg=msg)

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=body.model_dump(),
        )

    @app.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials_error(
        request: Request,
        exception: InvalidCredentialsError,
    ) -> JSONResponse:
        body = ErrorResponse(msg=str(exception))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=body.model_dump()
        )

    @app.exception_handler(MissingAccessTokenError)
    async def handle_missing_access_token_error(
        request: Request,
        exception: MissingAccessTokenError,
    ) -> JSONResponse:
        body = ErrorResponse(msg=str(exception))
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content=body.model_dump()
        )
