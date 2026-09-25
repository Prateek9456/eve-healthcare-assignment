"""Seed sample diagnostic centres for local demo."""

from app.database import SessionLocal
from app.models.centre import DiagnosticCentre, DiagnosticTest


def seed() -> None:
    db = SessionLocal()
    if db.query(DiagnosticCentre).count() > 0:
        print("Data already seeded.")
        db.close()
        return

    centres = [
        DiagnosticCentre(
            name="EVE Diagnostics Hauz Khas",
            location="Hauz Khas, New Delhi",
            tests=[
                DiagnosticTest(name="Complete Blood Count", price="499.00"),
                DiagnosticTest(name="Lipid Profile", price="799.00"),
            ],
        ),
        DiagnosticCentre(
            name="EVE Imaging Gurugram",
            location="Sector 44, Gurugram",
            tests=[
                DiagnosticTest(name="Chest X-Ray", price="599.00"),
                DiagnosticTest(name="MRI Brain", price="6999.00"),
            ],
        ),
    ]
    db.add_all(centres)
    db.commit()
    db.close()
    print("Seed data inserted.")


if __name__ == "__main__":
    seed()
