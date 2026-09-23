from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.db.models import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"
    __table_args__ = UniqueConstraint("slug", name="uq_categories_slug")

    name: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    slug: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    description: Mapped[str] = mapped_column(type_=Text(), nullable=True)
