"""Usage: uv run python -m app.scripts.seed_user <email> <password> <full_name>"""

import sys

from sqlmodel import Session

from app.core.security import hash_password
from app.db.session import engine
from app.modules.auth.service import get_user_by_email
from app.modules.auth.models import User


def main() -> None:
    email, password, full_name = sys.argv[1], sys.argv[2], sys.argv[3]

    with Session(engine) as session:
        if get_user_by_email(session, email) is not None:
            print(f"User {email} already exists")
            return

        user = User(email=email, password_hash=hash_password(password), full_name=full_name)
        session.add(user)
        session.commit()
        print(f"Created user {email}")


if __name__ == "__main__":
    main()
