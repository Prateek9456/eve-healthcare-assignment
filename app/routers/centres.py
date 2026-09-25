from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.centre import (
    CentreCreate,
    CentreResponse,
    PaginatedCentresResponse,
    TestCreate,
    TestResponse,
)
from app.services.centres import add_test_to_centre, create_centre, get_centre, list_centres

router = APIRouter(prefix="/centres", tags=["Diagnostic Centres"])


@router.post("", response_model=CentreResponse, status_code=201)
def create_diagnostic_centre(
    payload: CentreCreate, db: Session = Depends(get_db)
) -> CentreResponse:
    centre = create_centre(db, payload)
    return CentreResponse.model_validate(centre)


@router.get("", response_model=PaginatedCentresResponse)
def get_diagnostic_centres(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedCentresResponse:
    centres, total = list_centres(db, page, page_size)
    return PaginatedCentresResponse(
        items=[CentreResponse.model_validate(centre) for centre in centres],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{centre_id}", response_model=CentreResponse)
def get_diagnostic_centre(
    centre_id: int, db: Session = Depends(get_db)
) -> CentreResponse:
    centre = get_centre(db, centre_id)
    return CentreResponse.model_validate(centre)


@router.post("/{centre_id}/tests", response_model=TestResponse, status_code=201)
def create_test_for_centre(
    centre_id: int, payload: TestCreate, db: Session = Depends(get_db)
) -> TestResponse:
    test = add_test_to_centre(db, centre_id, payload)
    return TestResponse.model_validate(test)
