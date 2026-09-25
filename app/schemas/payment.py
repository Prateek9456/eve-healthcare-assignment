from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    booking_id: int = Field(gt=0)
    simulate_success: bool = True


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    amount: Decimal
    status: PaymentStatus
    provider_event_id: str | None
    created_at: datetime
    updated_at: datetime


class PaymentWebhookPayload(BaseModel):
    event_id: str = Field(min_length=1, max_length=255)
    booking_id: int = Field(gt=0)
    status: PaymentStatus
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
