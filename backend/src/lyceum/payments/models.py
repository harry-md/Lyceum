from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.courses.models import Course
from lyceum.db.models import BaseModel
from lyceum.users.models import User


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELED = "canceled"


class Order(BaseModel):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("order_number", name="uq_orders_order_number"),
        CheckConstraint("total_price >= 0", name="chk_orders_total_price"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(User.id), nullable=False, index=True
    )
    order_number: Mapped[str | None] = mapped_column(type_=String(255), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        type_=Enum(
            OrderStatus,
            name="order_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
    )
    currency: Mapped[str] = mapped_column(
        type_=String(3), nullable=False, default="VND"
    )
    total_price: Mapped[Decimal | None] = mapped_column(
        type_=Numeric(precision=10, scale=2), nullable=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )


class OrderDetail(BaseModel):
    __tablename__ = "order_details"
    __table_args__ = (
        UniqueConstraint("order_id", "course_id", name="uq_order_details_order_course"),
        CheckConstraint("price >= 0", name="chk_order_details_price"),
    )

    order_id: Mapped[UUID] = mapped_column(ForeignKey(Order.id), nullable=False)
    course_id: Mapped[UUID] = mapped_column(ForeignKey(Course.id), nullable=False)
    price: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=2), nullable=False
    )


class PaymentProvider(StrEnum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    ZALOPAY = "zalopay"


class PaymentStatus(StrEnum):
    CREATED = "created"
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    EXPIRED = "expired"


class Payment(BaseModel):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_checkout_id",
            name="uq_payments_provider_provider_checkout_id",
        ),
        UniqueConstraint(
            "provider",
            "provider_payment_id",
            name="uq_payments_provider_provider_payment_id",
        ),
        UniqueConstraint("merchant_reference", name="uq_payments_merchant_reference"),
        CheckConstraint("amount >= 0", name="chk_payments_amount"),
    )

    order_id: Mapped[UUID] = mapped_column(
        ForeignKey(Order.id), nullable=False, index=True
    )
    provider: Mapped[PaymentProvider] = mapped_column(
        type_=Enum(
            PaymentProvider,
            name="provider",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
    )
    merchant_reference: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    provider_checkout_id: Mapped[str | None] = mapped_column(
        type_=String(255), nullable=True
    )
    provider_payment_id: Mapped[str | None] = mapped_column(
        type_=String(255), nullable=True
    )
    status: Mapped[PaymentStatus] = mapped_column(
        type_=Enum(
            PaymentStatus,
            name="payment_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=PaymentStatus.CREATED,
        server_default=PaymentStatus.CREATED.value,
    )
    provider_status: Mapped[str | None] = mapped_column(
        type_=String(255), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=2), nullable=False
    )
    currency: Mapped[str] = mapped_column(type_=String(3), nullable=False)
    failure_code: Mapped[str | None] = mapped_column(type_=String(50), nullable=True)
    failure_message: Mapped[str | None] = mapped_column(
        type_=String(100), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
