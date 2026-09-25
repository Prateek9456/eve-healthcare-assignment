from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.booking import Booking, BookingStatus
from app.models.centre import DiagnosticCentre, DiagnosticTest
from app.models.user import User
from app.schemas.booking import BookingCreate


def create_booking(db: Session, user: User, payload: BookingCreate) -> Booking:
    if payload.appointment_at <= datetime.now(UTC):
        raise ConflictError("Appointment time must be in the future")

    test = (
        db.query(DiagnosticTest)
        .filter(DiagnosticTest.id == payload.test_id)
        .first()
    )
    if not test:
        raise NotFoundError("Diagnostic test not found")

    centre = (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.id == payload.centre_id)
        .first()
    )
    if not centre:
        raise NotFoundError("Diagnostic centre not found")

    if test.centre_id != centre.id:
        raise ConflictError("Selected test is not offered by the chosen centre")

    booking = Booking(
        user_id=user.id,
        test_id=test.id,
        centre_id=centre.id,
        appointment_at=payload.appointment_at,
        amount=test.price,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def get_booking(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise NotFoundError("Booking not found")
    return booking


def get_user_booking(db: Session, user: User, booking_id: int) -> Booking:
    booking = get_booking(db, booking_id)
    if booking.user_id != user.id:
        raise ForbiddenError("You do not have access to this booking")
    return booking


def cancel_booking(db: Session, user: User, booking_id: int) -> Booking:
    booking = get_user_booking(db, user, booking_id)
    if booking.status in {BookingStatus.CONFIRMED, BookingStatus.FAILED}:
        raise ConflictError(f"Cannot cancel a booking in {booking.status.value} status")
    if booking.status == BookingStatus.CANCELLED:
        raise ConflictError("Booking is already cancelled")

    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking
