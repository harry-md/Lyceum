class ResourceNotFoundError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class ForbiddenError(Exception):
    pass


class ConflictError(Exception):
    pass


class ImageUploadError(Exception):
    pass
