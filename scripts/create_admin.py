"""Create or promote an account to an administrator."""
import argparse
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import get_session_factory
from app.models import User
from app.security import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    email = args.email.strip().lower()
    if len(args.password.encode("utf-8")) > 72:
        parser.error("password must be at most 72 UTF-8 bytes for bcrypt")
    with get_session_factory()() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(name=args.name, email=email, password_hash=hash_password(args.password), role="admin")
            db.add(user)
            action = "created"
        else:
            user.name = args.name
            user.password_hash = hash_password(args.password)
            user.role = "admin"
            action = "promoted"
        db.commit()
        print(f"Admin {action}: {user.email} (id={user.id})")


if __name__ == "__main__":
    main()
