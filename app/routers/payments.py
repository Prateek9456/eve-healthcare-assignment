from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentWebhookPayload
from app.services.payments import create_payment, process_payment_webhook

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=201)
def simulate_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    payment = create_payment(db, current_user, payload)
    return PaymentResponse.model_validate(payment)


@router.post("/webhook", response_model=PaymentResponse)
def payment_webhook(
    payload: PaymentWebhookPayload, db: Session = Depends(get_db)
) -> PaymentResponse:
    payment, _ = process_payment_webhook(db, payload)
    return PaymentResponse.model_validate(payment)
