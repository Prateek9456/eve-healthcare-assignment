import logging
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentWebhookPayload

logger = logging.getLogger(__name__)


def _apply_payment_to_booking(booking: Booking, payment_status: PaymentStatus) -> None:
    if payment_status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED


def create_payment(
    db: Session, user: User, payload: PaymentCreate
) -> Payment:
    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise NotFoundError("Booking not found")
    if booking.user_id != user.id:
        raise ForbiddenError("You do not have access to this booking")
    if booking.status != BookingStatus.PENDING:
        raise ConflictError(
            f"Payment can only be initiated for PENDING bookings (current: {booking.status.value})"
        )

    payment_status = (
        PaymentStatus.SUCCESS if payload.simulate_success else PaymentStatus.FAILED
    )
    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=payment_status,
    )
    _apply_payment_to_booking(booking, payment_status)

    db.add(payment)
    db.commit()
    db.refresh(payment)
    logger.info(
        "Simulated payment processed",
        extra={"booking_id": booking.id, "payment_id": payment.id, "status": payment.status.value},
    )
    return payment


def process_payment_webhook(
    db: Session, payload: PaymentWebhookPayload
) -> tuple[Payment, bool]:
    existing = (
        db.query(Payment)
        .filter(Payment.provider_event_id == payload.event_id)
        .first()
    )
    if existing:
        logger.info(
            "Duplicate webhook ignored",
            extra={"event_id": payload.event_id, "payment_id": existing.id},
        )
        return existing, True

    booking = db.query(Booking).filter(Booking.id == payload.booking_id).first()
    if not booking:
        raise NotFoundError("Booking not found")

    if booking.amount != payload.amount:
        raise ConflictError("Webhook amount does not match booking amount")

    if booking.status not in {BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.FAILED}:
        raise ConflictError(
            f"Cannot process webhook for booking in {booking.status.value} status"
        )

    payment = Payment(
        booking_id=booking.id,
        amount=payload.amount,
        status=payload.status,
        provider_event_id=payload.event_id,
    )
    _apply_payment_to_booking(booking, payload.status)

    db.add(payment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(Payment)
            .filter(Payment.provider_event_id == payload.event_id)
            .first()
        )
        if existing:
            return existing, True
        raise

    db.refresh(payment)
    logger.info(
        "Webhook payment processed",
        extra={"event_id": payload.event_id, "payment_id": payment.id},
    )
    return payment, False
