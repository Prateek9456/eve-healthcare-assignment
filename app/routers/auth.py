from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.auth import authenticate_user, create_access_token, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    user = register_user(db, payload)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, payload.email, payload.password)
    token = create_access_token(user.id)
    return Token(access_token=token)
