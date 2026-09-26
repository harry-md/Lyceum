from sqlalchemy.exc import IntegrityError


def violated_constraint(error: IntegrityError) -> str | None:
    original = error.orig

    return getattr(original, "constraint_name", None) or getattr(
        getattr(original, "__cause__", None),
        "constraint_name",
        None,
    )
