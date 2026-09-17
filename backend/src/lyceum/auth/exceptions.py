class AccountAlreadyExistsError(Exception):
    def __init__(self, field: str | None = None) -> None:
        self.field = field
        super().__init__(field)


class InvalidCredentialsError(Exception):
    pass
