import argparse
import getpass

from database import LocalSession
import models.sqlAmodels as models
from psycopg_models import UserStatus
from services.cart_services import pwd_context


def main():
    parser = argparse.ArgumentParser(description="Create or promote a store administrator")
    parser.add_argument("email", help="Email address for the administrator account")
    email = parser.parse_args().email.strip().lower()

    db = LocalSession()
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is not None:
            if user.is_admin:
                print(f"{email} is already an administrator")
                return
            user.is_admin = True
            db.commit()
            print(f"Promoted {email} to administrator")
            return

        password = getpass.getpass("New admin password (12-72 bytes): ")
        confirmation = getpass.getpass("Confirm admin password: ")
        password_length = len(password.encode("utf-8"))
        if password != confirmation:
            raise ValueError("Passwords do not match")
        if not 12 <= password_length <= 72:
            raise ValueError("Admin password must be between 12 and 72 bytes")

        user = models.User(
            email=email,
            password_hash=pwd_context.hash(password),
            status=UserStatus.active,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        print(f"Created administrator account {email}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()