import logging

import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from starlette.concurrency import run_in_threadpool

from lyceum.core.config import Settings
from lyceum.shared.exceptions import ImageUploadError

logger = logging.getLogger(__name__)


def _upload_options(settings: Settings) -> dict[str, str | bool]:
    cloud_name = settings.cloudinary_cloud_name
    api_key = settings.cloudinary_api_key
    api_secret = settings.cloudinary_api_secret

    if (
        not cloud_name
        or not api_key
        or api_secret is None
        or not api_secret.get_secret_value()
    ):
        raise ImageUploadError("Chưa cấu hình đầy đủ Cloudinary")

    return {
        "cloud_name": cloud_name,
        "api_key": api_key,
        "api_secret": api_secret.get_secret_value(),
        "secure": True,
    }


async def upload_image(
    content: bytes,
    public_id: str,
    settings: Settings,
) -> str:
    try:
        options = _upload_options(settings)

        result = await run_in_threadpool(
            cloudinary.uploader.upload,
            content,
            public_id=public_id,
            resource_type="image",
            allowed_formats=["jpg", "png", "webp"],
            overwrite=False,
            timeout=30,
            **options,
        )
        return result["secure_url"]

    except (CloudinaryError, KeyError) as error:
        logger.error(
            "Cloudinary upload failed; public_id=%s",
            public_id,
        )
        raise ImageUploadError(
            "Không upload được ảnh; hãy kiểm tra ảnh hoặc thử lại sau"
        ) from error


async def delete_image(
    public_id: str,
    settings: Settings,
) -> None:
    try:
        result = await run_in_threadpool(
            cloudinary.uploader.destroy,
            public_id,
            resource_type="image",
            invalidate=True,
            timeout=15,
            **_upload_options(settings),
        )

        if result.get("result") not in {"ok", "not found"}:
            logger.error(
                "Cloudinary cleanup failed; public_id=%s",
                public_id,
            )

    except Exception:  # noqa: BLE001
        # Cleanup không được che mất lỗi lưu course ban đầu.
        logger.error(
            "Cloudinary cleanup failed; public_id=%s",
            public_id,
        )
