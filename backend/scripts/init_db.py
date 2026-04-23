from app.db.seed import seed_demo_data
from app.db.session import SessionLocal, init_db


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
