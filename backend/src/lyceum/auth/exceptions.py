class AccountAlreadyExistsError(Exception):
    def __init__(self, field: str | None = None) -> None:
        self.field = field
        super().__init__(field)


class InvalidCredentialsError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class MissingAccessTokenError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
