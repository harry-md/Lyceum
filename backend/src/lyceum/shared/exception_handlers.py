from fastapi import FastAPI, Request, status
from pydantic import ValidationError
from starlette.responses import JSONResponse

from lyceum.shared.exceptions import ResourceNotFoundError
from lyceum.shared.schemas import ErrorResponse


def register_shared_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ResourceNotFoundError)
    async def handle_resource_not_found_error(
        request: Request,
        exception: ResourceNotFoundError,
    ) -> JSONResponse:
        body = ErrorResponse(msg=str(exception))

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=body.model_dump(),
        )
