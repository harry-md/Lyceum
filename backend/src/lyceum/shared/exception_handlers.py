from fastapi import FastAPI, Request, status
from starlette.responses import JSONResponse

from lyceum.shared.exceptions import (
    ConflictError,
    ForbiddenError,
    ImageUploadError,
    ResourceNotFoundError,
)
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

    @app.exception_handler(ForbiddenError)
    async def handle_forbidden(
        request: Request,
        exception: ForbiddenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"msg": str(exception)},
        )

    @app.exception_handler(ConflictError)
    async def handle_conflict(
        request: Request,
        exception: ConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"msg": str(exception)},
        )

    @app.exception_handler(ImageUploadError)
    async def handle_image_upload_error(
        request: Request,
        exception: ImageUploadError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"msg": str(exception)},
        )
