from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

from lyceum.auth.exceptions import AccountAlreadyExistsError
from lyceum.auth.schemas import ErrorResponse


def register_auth_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AccountAlreadyExistsError)
    async def account_already_exists_handler(
        _request: Request,
        exception: AccountAlreadyExistsError,
    ) -> JSONResponse:
        if exception.field is not None:
            message = f"{exception.field} đã tồn tại"
        else:
            message = "Username hoặc email đã tồn tại"

        body = ErrorResponse(message=message)

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=body.model_dump(),
        )
