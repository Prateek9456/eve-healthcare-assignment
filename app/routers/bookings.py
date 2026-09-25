from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.bookings import cancel_booking, create_booking, get_user_booking

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, status_code=201)
def create_diagnostic_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingResponse:
    booking = create_booking(db, current_user, payload)
    return BookingResponse.model_validate(booking)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingResponse:
    booking = get_user_booking(db, current_user, booking_id)
    return BookingResponse.model_validate(booking)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_diagnostic_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookingResponse:
    booking = cancel_booking(db, current_user, booking_id)
    return BookingResponse.model_validate(booking)
