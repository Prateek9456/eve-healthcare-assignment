from sqlalchemy.orm import Session, selectinload

from app.exceptions import NotFoundError
from app.models.centre import DiagnosticCentre, DiagnosticTest
from app.schemas.centre import CentreCreate, TestCreate


def create_centre(db: Session, payload: CentreCreate) -> DiagnosticCentre:
    centre = DiagnosticCentre(name=payload.name, location=payload.location)
    centre.tests = [
        DiagnosticTest(name=test.name, price=test.price) for test in payload.tests
    ]
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


def add_test_to_centre(
    db: Session, centre_id: int, payload: TestCreate
) -> DiagnosticTest:
    centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
    if not centre:
        raise NotFoundError("Diagnostic centre not found")

    test = DiagnosticTest(centre_id=centre_id, name=payload.name, price=payload.price)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


def get_centre(db: Session, centre_id: int) -> DiagnosticCentre:
    centre = (
        db.query(DiagnosticCentre)
        .options(selectinload(DiagnosticCentre.tests))
        .filter(DiagnosticCentre.id == centre_id)
        .first()
    )
    if not centre:
        raise NotFoundError("Diagnostic centre not found")
    return centre


def list_centres(db: Session, page: int, page_size: int) -> tuple[list[DiagnosticCentre], int]:
    query = db.query(DiagnosticCentre).options(selectinload(DiagnosticCentre.tests))
    total = query.count()
    centres = (
        query.order_by(DiagnosticCentre.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return centres, total
